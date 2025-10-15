from __future__ import annotations

import json
import asyncio
import aiohttp
from aiohttp import ClientSession, ClientTimeout

from ..typing import AsyncResult, Messages
from .base_provider import AsyncGeneratorProvider, ProviderModelMixin
from ..errors import ResponseError

class Ollama(AsyncGeneratorProvider, ProviderModelMixin):
    """
    Custom provider for Ollama server integration.
    Connects to a private Ollama server for model inference.
    """

    url = "http://100.92.194.37:11434"
    api_endpoint = f"{url}/api/chat"
    models_endpoint = f"{url}/api/tags"

    working = True
    supports_stream = True
    supports_system_message = True
    supports_message_history = True

    default_model = "deepseek-r1:14b" #"llama3.1:8b"
    models = []

    @classmethod
    def get_models(cls, **kwargs) -> list[str]:
        """
        Fetch available models from Ollama server.

        Returns:
            list[str]: List of available model names
        """
        if not cls.models:
            try:
                import requests
                response = requests.get(cls.models_endpoint, timeout=5)
                response.raise_for_status()
                data = response.json()

                # Extract model names from response
                if "models" in data:
                    cls.models = [model["name"] for model in data["models"]]

                # Fallback to default if no models found
                if not cls.models:
                    cls.models = [cls.default_model]

            except Exception as e:
                # Fallback to default model on error
                cls.models = [cls.default_model]

        return cls.models

    @classmethod
    async def create_async_generator(
        cls,
        model: str,
        messages: Messages,
        stream: bool = True,
        proxy: str = None,
        timeout: int = 120,
        **kwargs
    ) -> AsyncResult:
        """
        Generate responses from Ollama server.

        Args:
            model (str): Model name to use
            messages (Messages): List of message dictionaries
            stream (bool): Whether to stream responses
            proxy (str): Proxy URL if needed
            timeout (int): Request timeout in seconds
            **kwargs: Additional arguments

        Yields:
            str: Response chunks from the model
        """
        # Ensure models are loaded
        if not cls.models:
            cls.get_models()

        # Use model from cls.get_model() for validation
        model = cls.get_model(model)

        # Format messages for Ollama API
        formatted_messages = []
        for message in messages:
            formatted_messages.append({
                "role": message["role"],
                "content": message["content"]
            })

        # Prepare request data
        data = {
            "model": model,
            "messages": formatted_messages,
            "stream": stream
        }

        # Add optional parameters if provided
        if "temperature" in kwargs:
            data.setdefault("options", {})["temperature"] = kwargs["temperature"]
        if "top_p" in kwargs:
            data.setdefault("options", {})["top_p"] = kwargs["top_p"]
        if "max_tokens" in kwargs:
            data.setdefault("options", {})["num_predict"] = kwargs["max_tokens"]

        headers = {
            "Content-Type": "application/json"
        }

        # Set timeout
        client_timeout = ClientTimeout(total=timeout)

        try:
            async with ClientSession(timeout=client_timeout) as session:
                async with session.post(
                    cls.api_endpoint,
                    headers=headers,
                    json=data,
                    proxy=proxy
                ) as response:
                    response.raise_for_status()

                    if stream:
                        # Stream response line by line
                        async for line in response.content:
                            if line:
                                try:
                                    # Parse NDJSON response
                                    json_response = json.loads(line)

                                    # Extract message content
                                    if "message" in json_response:
                                        content = json_response["message"].get("content", "")
                                        if content:
                                            yield content

                                    # Check if done
                                    if json_response.get("done", False):
                                        break

                                except json.JSONDecodeError:
                                    # Skip malformed JSON lines
                                    continue
                                except Exception as e:
                                    raise ResponseError(f"Error parsing response: {e}")
                    else:
                        # Non-streaming response
                        result = await response.json()
                        if "message" in result:
                            yield result["message"].get("content", "")
                        else:
                            raise ResponseError(f"Invalid response format: {result}")

        except aiohttp.ClientError as e:
            raise ResponseError(f"Ollama server error: {e}")
        except asyncio.TimeoutError:
            raise ResponseError(f"Ollama server timeout after {timeout}s")
        except Exception as e:
            raise ResponseError(f"Unexpected error: {e}")

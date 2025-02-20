from os import getenv
from ..api_service.services.base_service import BaseService
from ..api_service.end_points.payload_package import PayloadCreation

class AnthropicService(BaseService):
    """
    A service to interact with Anthropic's API endpoints.

    Attributes:
        base_url (str): The base URL for the Anthropic API.
        available_endpoints (list): A list of available API endpoints.
        schema (dict): The schema configuration for the API.
        key_scheme (str): The environment variable name for Anthropic API key.
        token_encoding_name (str): The default token encoding scheme.

    Examples:
        >>> service = AnthropicService(api_key="your_api_key")
        >>> asyncio.run(service.serve("Hello, world!", "chat/completions"))
        (payload, completion)
    """

    base_url = "https://api.anthropic.com/v1/"
    available_endpoints = ['chat/completions']
    schema = {}        # TODO
    key_scheme = "ANTHROPIC_API_KEY"
    token_encoding_name = "cl100k_base"

    def __init__(self, api_key = None, key_scheme = None,schema = None, token_encoding_name: str = "cl100k_base", **kwargs):
        key_scheme = key_scheme or self.key_scheme            
        super().__init__(
            api_key = api_key or getenv(key_scheme),
            schema = schema or self.schema,
            token_encoding_name=token_encoding_name, 
            **kwargs
        )
        self.active_endpoint = []

    async def serve(self, input_, endpoint="chat/completions", method="post", **kwargs):
        """
        Serves the input using the specified endpoint and method.

        Args:
            input_: The input text to be processed.
            endpoint: The API endpoint to use for processing.
            method: The HTTP method to use for the request.
            **kwargs: Additional keyword arguments to pass to the payload creation.

        Returns:
            A tuple containing the payload and the completion response from the API.
        """
        if endpoint not in self.active_endpoint:
            await self. init_endpoint(endpoint)
        if endpoint == "chat/completions":
            return await self.serve_chat(input_, **kwargs)
        else:
            return ValueError(f'{endpoint} is currently not supported')
    
    async def serve_chat(self, messages, **kwargs):
        """
        Serves the chat completion request with the given messages.

        Args:
            messages: The messages to be included in the chat completion.
            **kwargs: Additional keyword arguments for payload creation.

        Returns:
            A tuple containing the payload and the completion response from the API.
        """
        if "chat/completions" not in self.active_endpoint:
            await self. init_endpoint("chat/completions")
            self.active_endpoint.append("chat/completions")
        payload = PayloadCreation.chat_completion(
            messages, self.endpoints["chat/completions"].config, self.schema["chat/completions"], **kwargs)

        try:
            completion = await self.call_api(payload, "chat/completions", "post")
            return payload, completion
        except Exception as e:
            self.status_tracker.num_tasks_failed += 1
            raise e

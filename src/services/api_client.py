"""
API Client for Guard AI Security System
"""
import requests
from typing import Dict, Any, Optional
from exceptions import GuardApiError, ServiceUnavailableError


class ApiClient:
    """Handles HTTP API communications with retry logic and error handling"""
    
    def __init__(self, nemoguardrails_url: str = "http://127.0.0.1:5070", 
                 ollama_url: str = "http://127.0.0.1:11434",
                 timeout: int = 120):
        """Initialize API client
        
        Args:
            nemoguardrails_url: URL for NeMo Guardrails API
            ollama_url: URL for Ollama API  
            timeout: Request timeout in seconds
        """
        self.nemoguardrails_url = nemoguardrails_url.rstrip('/')
        self.ollama_url = ollama_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
        
        # Configure session for better performance
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=10,
            pool_maxsize=20,
            max_retries=3
        )
        self.session.mount('http://', adapter)
        self.session.mount('https://', adapter)
    
    def check_service_availability(self, service_url: str, service_name: str) -> bool:
        """Check if a service is available
        
        Args:
            service_url: URL of the service to check
            service_name: Name of the service for error reporting
            
        Returns:
            True if service is available
            
        Raises:
            ServiceUnavailableError: If service is not available
        """
        try:
            response = self.session.get(f"{service_url}/health", timeout=5)
            return response.status_code == 200
        except:
            # Try alternative endpoints for specific services
            if 'nemoguardrails' in service_name.lower():
                try:
                    response = self.session.get(f"{service_url}/v1/rails/configs", timeout=5)
                    return response.status_code == 200
                except:
                    pass
            elif 'ollama' in service_name.lower():
                try:
                    response = self.session.get(f"{service_url}/api/tags", timeout=5)
                    return response.status_code == 200
                except:
                    pass
            
            raise ServiceUnavailableError(service_name, service_url)
    
    def request_nemoguardrails_multi_configs(self, user_input: str, config_ids: list[str], 
                            options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make request to NeMo Guardrails server
        
        Args:
            user_input: User input message
            config_id: Configuration ID to use
            options: Additional options for the request
            
        Returns:
            Response data from NeMo Guardrails
            
        Raises:
            GuardApiError: If request fails
        """
        if options is None:
            options = {
                "llm_output": True,
                "log": {
                    "activated_rails": True,
                    "llm_calls": True,
                    "colang_history": True,
                }
            }
        
        payload = {
            "config_ids": config_ids,
            "messages": [{
                "role": "user",
                "content": user_input
            }],
            "options": options
        }
        
        try:
            response = self.session.post(
                f"{self.nemoguardrails_url}/v1/chat/completions",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.Timeout:
            raise GuardApiError(f"NeMo Guardrails request timeout after {self.timeout}s")
        except requests.exceptions.ConnectionError:
            raise GuardApiError("Failed to connect to NeMo Guardrails service")
        except requests.exceptions.HTTPError as e:
            error_msg = f"NeMo Guardrails HTTP error: {e.response.status_code}"
            raise GuardApiError(error_msg, e.response.status_code)
        except Exception as e:
            raise GuardApiError(f"NeMo Guardrails request failed: {str(e)}")
        
    def request_nemoguardrails_single_config(self, user_input: str, config_id: str, 
                            options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Make request to NeMo Guardrails server
        
        Args:
            user_input: User input message
            config_id: Configuration ID to use
            options: Additional options for the request
            
        Returns:
            Response data from NeMo Guardrails
            
        Raises:
            GuardApiError: If request fails
        """
        if options is None:
            options = {
                "llm_output": True,
                "log": {
                    "activated_rails": True,
                    "llm_calls": True,
                    "colang_history": True,
                }
            }
        
        payload = {
            "config_id": config_id,
            "messages": [{
                "role": "user",
                "content": user_input
            }],
            "options": options
        }
        
        try:
            response = self.session.post(
                f"{self.nemoguardrails_url}/v1/chat/completions",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.Timeout:
            raise GuardApiError(f"NeMo Guardrails request timeout after {self.timeout}s")
        except requests.exceptions.ConnectionError:
            raise GuardApiError("Failed to connect to NeMo Guardrails service")
        except requests.exceptions.HTTPError as e:
            error_msg = f"NeMo Guardrails HTTP error: {e.response.status_code}"
            raise GuardApiError(error_msg, e.response.status_code)
        except Exception as e:
            raise GuardApiError(f"NeMo Guardrails request failed: {str(e)}")
    
    def request_ollama(self, user_input: str, model: str = "qwen3:30b-instruct", 
                      stream: bool = False) -> Dict[str, Any]:
        """Make direct request to Ollama
        
        Args:
            user_input: User input message
            model: Model name to use
            stream: Whether to use streaming
            
        Returns:
            Response data from Ollama
            
        Raises:
            GuardApiError: If request fails
        """
        payload = {
            "model": model,
            "prompt": user_input,
            "stream": stream
        }
        
        try:
            response = self.session.post(
                f"{self.ollama_url}/api/generate",
                json=payload,
                timeout=self.timeout - 30  # Ollama typically faster
            )
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.Timeout:
            raise GuardApiError(f"Ollama request timeout after {self.timeout - 30}s")
        except requests.exceptions.ConnectionError:
            raise GuardApiError("Failed to connect to Ollama service")
        except requests.exceptions.HTTPError as e:
            error_msg = f"Ollama HTTP error: {e.response.status_code}"
            raise GuardApiError(error_msg, e.response.status_code)
        except Exception as e:
            raise GuardApiError(f"Ollama request failed: {str(e)}")
    
    def get_nemoguardrails_configs(self) -> Dict[str, Any]:
        """Get available NeMo Guardrails configurations
        
        Returns:
            Available configurations
            
        Raises:
            GuardApiError: If request fails
        """
        try:
            response = self.session.get(f"{self.nemoguardrails_url}/v1/rails/configs", timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise GuardApiError(f"Failed to get NeMo Guardrails configs: {str(e)}")
    
    def get_ollama_models(self) -> Dict[str, Any]:
        """Get available Ollama models
        
        Returns:
            Available models
            
        Raises:
            GuardApiError: If request fails
        """
        try:
            response = self.session.get(f"{self.ollama_url}/api/tags", timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            raise GuardApiError(f"Failed to get Ollama models: {str(e)}")
    
    def close(self):
        """Close the session and cleanup resources"""
        if self.session:
            self.session.close()

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource
from nemoguardrails import LLMRails, RailsConfig

# Configure OpenTelemetry
resource = Resource.create({"service.name": "guardrails-quickstart"})
tracer_provider = TracerProvider(resource=resource)
trace.set_tracer_provider(tracer_provider)
tracer_provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

# Configure guardrails with tracing
config_yaml = """
models:
  - type: main
    engine: ollama
    model: gpt-oss:20b
rails:
  config:
    streaming: true

tracing:
  enabled: true
  adapters:
    - name: OpenTelemetry
"""

config = RailsConfig.from_content(yaml_content=config_yaml)
rails = LLMRails(config)
response = rails.generate(messages=[{"role": "user", "content": "Hello!"}])
print(f"Response: {response}")
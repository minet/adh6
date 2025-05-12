from adh6.server import init

# from opentelemetry import trace
# from opentelemetry.instrumentation.flask import FlaskInstrumentor

# from opentelemetry.exporter.jaeger.thrift import JaegerExporter
# from opentelemetry.sdk.resources import SERVICE_NAME, Resource
# from opentelemetry.sdk.trace import TracerProvider
# from opentelemetry.sdk.trace.export import BatchSpanProcessor

# tracer = trace.get_tracer(__name__)
application = init()
# FlaskInstrumentor().instrument_app(application.app)


# # TODO: comprendre à quoi ça servait, et voir si c'était important
# def post_fork(server, worker):
#     server.log.info("Worker spawned (pid: %s)", worker.pid)
#     server.log.info("test")
#     resource = Resource.create(attributes={SERVICE_NAME: "api-service"})

#     trace.set_tracer_provider(TracerProvider(resource=resource))
#     # create a JaegerExporter
#     jaeger_exporter = JaegerExporter(
#         # configure agent
#         agent_host_name='jaeger',
#         agent_port=6831,
#         # optional: configure also collector
#         # collector_endpoint='http://localhost:14268/api/traces?format=jaeger.thrift',
#         # username=xxxx, # optional
#         # password=xxxx, # optional
#         # max_tag_value_length=None # optional
#     )

#     # This uses insecure connection for the purpose of example. Please see the
#     # OTLP Exporter documentation for other options.
#     span_processor = BatchSpanProcessor(jaeger_exporter)
#     trace.get_tracer_provider().add_span_processor(span_processor)

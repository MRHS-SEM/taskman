from projen.python import PythonProject

project = PythonProject(
    author_email="nico@nicolas-byl.io",
    author_name="Nicolas Byl",
    module_name="taskman",
    name="taskman",
    version="0.1.0",
    deps=[
        'fastapi',
        'google-cloud-storage',
        'redis',
        'uvicorn[standard]',
        'opentelemetry-api',
        'opentelemetry-sdk',
        'opentelemetry-instrumentation-fastapi',
        'opentelemetry-exporter-gcp-trace'
    ],
    dev_deps=[
        'attrs',
        'pylint',
        'pytest',
        'pytest-cov',
        'pytest-xdist',
        'fakeredis[json]'
    ],
    github=False,
)

project.add_git_ignore('.idea')

# Add the command to start Redis container to your project
redis_task = project.add_task("redis")
redis_task.exec('docker run -d -p 6379:6379 redis')

dev_task = project.add_task('dev')
dev_task.exec('uvicorn taskman.main:app --reload')

project.synth()

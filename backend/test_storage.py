from app.services.storage import upload_file, get_public_url

content = b"hello sitebuilt"

upload_file(
    bucket="plans",
    path="test/hello.txt",
    content=content,
    content_type="text/plain",
)

url = get_public_url("plans", "test/hello.txt")
print(url)

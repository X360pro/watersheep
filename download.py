import requests, zipfile, io, subprocess
zip_file_url = "https://ai-hackathon-upload.s3.ap-south-1.amazonaws.com/public/data.zip"
r = requests.get(zip_file_url)
z = zipfile.ZipFile(io.BytesIO(r.content))
z.extractall()

subprocess.call(['mv', '/data/*', '/watersheep/clips/'])


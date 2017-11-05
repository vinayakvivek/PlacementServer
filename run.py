from server import app
from local import URL, PORT

app.run(host=URL, port=int(PORT), debug=True)

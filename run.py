from dotenv import load_dotenv

load_dotenv()

from app import create_app
from app.config import Config

app = create_app()
print(Config.KEYCLOAK_URL)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=Config.SERVER_PORT, debug=Config.DEBUG_SERVER)
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Startet den Server auf Port 9099 (zum Test)
    app.run(host='0.0.0.0', port=9099, debug=True)
from app import create_app

app = create_app()

if __name__ == "__main__":
    print(app.template_folder)
    app.run(debug=True)
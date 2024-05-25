from hkabtrak import create_app
app = create_app('prod.conf')
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=1473)

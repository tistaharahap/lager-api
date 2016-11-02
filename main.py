from qb import app

print('Lager is being poured..')

if __name__ == '__main__':
    app.run(host='0.0.0.0',
            port=5000,
            debug=True)

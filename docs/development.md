# Development

## Environment

While developing, you can use `docker-compose` in order to host a temporary database for testing purposes.

```
docker-compose up -d
```

You can then use the Flask built-in development server.

```
python3 app.py
```

## Code formatting

Ptarmigan uses the code formatter [black](https://github.com/psf/black). Run it before comitting.

```
black .
```

## Releases

Ptarmigan uses the semantic versioning convention.
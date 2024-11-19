# Matrix Bot for sending homeserver invitation link via e-mail

A early stage and simlpe Matrix bot which I use in addition to [matrix-registration](https://github.com/ZerataX/matrix-registration).

The bot calls the Api and sends the invitation link via e-mail to a given receipient.

## Usage

Use container image or run this after cloning. In both cases you need to create a `.env` file containing the matrix and mail server credentials:

```
cp. .env.example .env
```

If you want to run it without the container you can run it like this:


```
. bin/activate
python -m matrix_bot_invitation_mailer
```

And for use with docker run it like this:

```
docker compose up -d
```

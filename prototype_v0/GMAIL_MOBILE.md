# Gmail configuration for PAE Mobile

PAE reads Gmail configuration from environment variables. `start-mobile.sh` also
loads a local file at `~/.config/pae/gmail.env` when it exists. This file is outside
the Git repository and must never be committed.

Required values:

```sh
PAE_GMAIL_ACCOUNT=your-account@example.com
PAE_GMAIL_CLIENT_ID=...
PAE_GMAIL_CLIENT_SECRET=...
PAE_GMAIL_REFRESH_TOKEN=...
```

The refresh token must have these Google OAuth scopes:

```text
https://www.googleapis.com/auth/gmail.readonly
https://www.googleapis.com/auth/gmail.compose
```

`gmail.readonly` supports live search and read. `gmail.compose` supports creating
drafts and sending the explicitly confirmed pending draft. A previously issued
read-only refresh token cannot create or send drafts; it must be reauthorized with
the additional scope.

Create the file on the phone and restrict it:

```sh
mkdir -p ~/.config/pae
chmod 700 ~/.config/pae
chmod 600 ~/.config/pae/gmail.env
```

Do not paste any secret value into chat, source code, Git, logs or screenshots.

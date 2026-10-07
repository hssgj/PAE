# GitHub configuration for PAE Mobile

Public-repository `github_list` and `github_read` work without a token. Search has
a bounded single-repository fallback without authentication. Authenticated code
search and all writes use `PAE_GITHUB_TOKEN`.

`start-mobile.sh` loads this optional local file, which is outside the repository:

```text
~/.config/pae/github.env
```

Its content is one line:

```sh
PAE_GITHUB_TOKEN=...
```

Use a fine-grained GitHub token limited to the intended repositories. Read-only use
needs repository contents/metadata read access. The confirmed single-file write path
needs repository contents read/write access on the designated test repository.

Protect the file:

```sh
mkdir -p ~/.config/pae
chmod 700 ~/.config/pae
chmod 600 ~/.config/pae/github.env
```

Never put the token into Git, chat, screenshots or runtime logs.

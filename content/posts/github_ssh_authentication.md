---
title: "Github SSH Authentication"
author: "Edmund Goodman"
date: 2024-12-17T19:28:56Z
draft: true
---

## Why do I need to do this?

From August 2021, GitHub announced they would not be allowing password authentication
when using the command line [^1].

<!--more-->

This means that in order to interact with GitHub from the command line you have
to use another authentication method.

This blog post enumerates the process of
configuring `git` and GitHub to use SSH keys, and some tips to streamline their
day-to-day usage. It is also available as a
[gist](https://gist.github.com/EdmundGoodman/e8faa0b3c2dddf350a00fb23dab48a59).

##  Using SSH keys

SSH keys are one of the authentication methods that can be used instead of
passwords. Atlassian defines them as follows:

> SSH keys are generated through a public key cryptographic algorithm, the most
> common being RSA or DSA. At a very high level SSH keys are generated through a
> mathematical formula that takes 2 prime numbers and a random seed variable to
> output the public and private key. This is a one-way formula that ensures the
> public key can be derived from the private key but the private key cannot be
> derived from the public key.
>
> -- Atlassian [^2]

### Why should I use SSH keys?

SSH keys provide a number of benefits over traditional password authentication,
which motivated its disablement for the command line. These include being
unique, revocable, limited, and random [^3].

Another alternative to authenticate to GitHub is token authentication, as
discussed in [an earlier blog post]({{<ref "/posts/github_token_authentication" >}}).
However, this approach comes with a number of drawbacks including only
providing access to the repositories rather than account settings and having
the option of password protection, making them much more secure even if leaked [^4].

### How do I use SSH keys?

The process for creating and using SSH keys is enumerated in the
[GitHub documentation](https://docs.github.com/en/authentication/connecting-to-github-with-ssh),
and summarised below:

1. Check if any SSH keys already exist with

   ```bash
   ls -al ~/.ssh
   ```

   If the directory exists and contains a pair of public and private key files
   (look for files called `id_rsa.pub`, `id_ecdsa.pub`, `id_ed25519.pub` or similar),
   you may choose to re-use these in step 3.

2. If not, generate a new key with

    ```bash
    ssh-keygen -t ed25519 -C "your_email@example.com"
    ```

    This will then prompt you to pick an algorithm (the default is probably
    sensible), and a passphrase (pick a long and secure one, as on MacOS this
    can be stored in the keychain and filled automatically, as discussed
    [in a later section]({{<ref "#avoiding-password-prompts-on-macos" >}})).

3. Add the key to `ssh-agent`

    ```bash
    eval "$(ssh-agent -s)"
    ```

    Which should output something similar to "`> Agent pid 59566`".

4. Update your `~/.ssh/config` file with `vi` [^5] 

    ```bash
    vi ~/.ssh/config
    ```
   to contain the following entry

   ```
   Host github.com
       AddKeysToAgent yes
       IdentityFile ~/.ssh/id_ed25519
   ```

   This can be modified to auto-fill on MacOS using the keychain, as discussed
   [in a later section]({{<ref "#avoiding-password-prompts-on-macos" >}})).

5. Add the key as an authentication method to GitHub, by copying the public key
   file

   ```bash
   cat ~/.ssh/id_ed25519.pub
   ```

    then add it as a new authentication SSH key to GitHub with the form at
    <https://github.com/settings/ssh/new>, with a meaningful title and the copied
    public key

    {{< figure
        src="/images/posts/github_ssh_authentication/create_key.png"
        alt="A screenshot of adding a SSH authentication key to GitHub"
        caption="A screenshot of adding a SSH authentication key to GitHub." >}}

    This will then show on the [GitHub SSH keys page](https://github.com/settings/keys).

    {{< figure
        src="/images/posts/github_ssh_authentication/authentication_keys.png"
        alt="A screenshot of added keys on the GitHub SSH keys page"
        caption="A screenshot of added keys on the GitHub SSH keys page." >}}

### Tips and gotchas

When using SSH keys, there are a couple of things which can make your life
easier/harder. Some of them I have encountered are enumerated below.

#### Avoiding password prompts on MacOS

On MacOS, the SSH key password can be added to the user keychain, significantly
reducing the friction when interacting with the remote. This step is listed in
the GitHub docs for MacOS, first updating the SSH config file as follows [^6].

```text
Host github.com
  AddKeysToAgent yes
  UseKeychain yes
  IdentityFile ~/.ssh/id_ed25519
```

Then, using the following command when adding the SSH key:

```bash
ssh-add --apple-use-keychain ~/.ssh/id_ed25519
```

#### Correctly configuring remotes

An easy point of confusion when using SSH keys is that different remotes are
required than when authenticating over HTTPS. For HTTPS, remotes tend to look
like:

```text
https://github.com/<USERNAME>/<REPOSITORY>
```

But when using SSH keys, remotes must be of the following format:

```text
git@github.com:<USERNAME>/<REPOSITORY>
```

As such, you may need to modify some repository remotes if switching from HTTPS
to SSH authentication. This can be done as follows, for the example of the `origin` remote:

```bash
git remote remove origin
git remote add origin git@github.com:<USERNAME>/<REPOSITORY>
```

#### Automatically using SSH remote URLs

To address [the above issue]({{<ref "#correctly-configuring-remotes" >}}), you
can configure `git` to rewrite HTTPS to SSH remote sources as follows [^7].

```bash
git config --global url.ssh://git@github.com/.insteadOf https://github.com/
```

However, this presents the possibility of difficult-to-debug errors with remotes,
so care should be taken if it is set.

#### Using an SSH key to sign commits

In addition to authenticating with, you can sign commits with your SSH key, with
instructions for doing this [available here](https://docs.github.com/en/authentication/managing-commit-signature-verification/telling-git-about-your-signing-key#telling-git-about-your-ssh-key).

First, you then need to add your SSH key as a "Signing key" (separate from an
"Authentication key", but on the same page) to GitHub with the form at
<https://github.com/settings/ssh/new>. This is the same process as
[adding an authentication key]({{<ref "#how-do-i-use-ssh-keys" >}}),
but the key type must be set as a signing key, as shown below. This will then
show on the [GitHub SSH keys page](https://github.com/settings/keys).

{{< figure
    src="/images/posts/github_ssh_authentication/signing_keys.png"
    alt="A screenshot of added keys on the GitHub SSH keys page"
    caption="A screenshot of added keys on the GitHub SSH keys page." >}}

Then, you can configure `git` to use the SSH key for signing all commits and tags.

```bash
git config --global gpg.format ssh
git config --global user.signingkey ~/.ssh/id_ed25519
git config --global commit.gpgsign true
git config --global tag.gpgSign true
```

Finally, this will then mark new signed commits as verified on GitHub, as shown
below:

{{< figure
    src="/images/posts/github_ssh_authentication/verified_commits.png"
    alt="A screenshot of verified commits shown in a GitHub history"
    caption="A screenshot of verified commits shown in a GitHub history." >}}


## References

[^1]: <https://github.blog/changelog/2021-08-12-git-password-authentication-is-shutting-down/>
[^2]: <https://www.atlassian.com/git/tutorials/git-ssh>
[^3]: <https://github.blog/security/application-security/token-authentication-requirements-for-git-operations/#background>
[^4]: <https://stackoverflow.com/a/37095306>
[^5]: <https://stackoverflow.com/a/11828573>
[^6]: <https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent#adding-your-ssh-key-to-the-ssh-agent>
[^7]: <https://stackoverflow.com/a/22027731>

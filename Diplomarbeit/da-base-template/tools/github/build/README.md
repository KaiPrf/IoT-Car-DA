# Build and send diploma thesis

The workflow `Build and send diploma thesis` allows the user to build the diploma thesis via a GitHub workflow and send it somwhere (e.g. to a Microsoft Teams channel). The built diploma thesis can also be downloaded as a [GitHub Action workflow artifact](https://docs.github.com/en/actions/managing-workflow-runs-and-deployments/managing-workflow-runs/downloading-workflow-artifacts).

## Microsoft Teams

1. [Create your own team](https://support.microsoft.com/en-us/office/create-and-organize-teams-ea9aa9c2-ae29-44ca-b838-4424b4daa44d) for the diploma thesis.
2. [Create a new channel](https://support.microsoft.com/en-us/office/create-a-standard-private-or-shared-channel-in-microsoft-teams-fda0b75e-5b90-4fb8-8857-7e102b014525) in your team preferably named `build`.
3. Get the channels [email address](https://support.microsoft.com/en-us/office/tip-send-email-to-a-channel-2c17dbae-acdf-4209-a761-b463bdaaa4ca).

## GitHub

### Repository

Create a folder `.github/workflows` in the root of your repository. You can now choose between `diploma-thesis-manual.yml`, `diploma-thesis-docker.yml` and `diploma-thesis-action.yml` to paste into the newly created folder. It is recommended to rename the chosen GitHub Action variant to `thesis.yml`.

- **-manual**
  - installs all the dependencies in the Action itself
  - runtime: ~10 minutes
- **-docker**
  - uses the Docker image
  - runtime: ~3 minutes
- **-action**
  - uses the published GitHub Action provided by the [`da-base-template`](https://github.com/HTL-Leoben/da-base-template) repository
  - runtime: ~3 minutes

The variants `diploma-thesis-manual.yml` and `diploma-thesis-docker.yml` each contain a [job](https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/using-jobs-in-a-workflow#overview) named `send`. This job can be deleted if the diploma thesis should only be built and not sent. Note, that the whole workflow will fail if the diploma thesis file size is too large when sending it, or if any input parameter is incorrect. Regarding the first case, a fix would be either to reduce the size of included images and PDFs or not use the send option. Regardless, the built diploma thesis is always saved as an [artifact](https://docs.github.com/en/actions/writing-workflows/choosing-what-your-workflow-does/storing-and-sharing-data-from-a-workflow#about-workflow-artifacts) in the latest **successful** workflow run.

### Inputs

This section is only relevant if the file `diploma-thesis-action.yml` is used.

| Name | Required | Description | Default |
| - | - | - | - |
| mail | `false` | The email address from which the diploma thesis should be sent from. See [notes](#notes). <br> Required if the diploma thesis should be sent somewhere (e.g. Microsoft Teams). | - |
| mail-password | `false` | The password for your email address. See [notes](#notes). <br> Required if the diploma thesis should be sent somewhere (e.g. Microsoft Teams). | - |
| smtp-server | `false` | The SMTP server URL corresponding to your email address. <br> Required if the diploma thesis should be sent somewhere (e.g. Microsoft Teams). | - |
| smtp-port | `false` | The SMTP port corresponding to your SMTP server. <br> Required if the diploma thesis should be sent somewhere (e.g. Microsoft Teams). | - |
| receiving-mail | `false` | Required if the diploma thesis should be sent somewhere (e.g. Microsoft Teams). <br> If the desired recipient is a Microsoft Teams channel, use its channel email address. | - |
| mail-body | `false` | Change the email body (e.g. the message in Microsoft Teams). | [`git log -1 --pretty=%B`](https://git-scm.com/docs/git-log) |
| thesis-path | `false` | Change the folder name where the template is located. | Diplomarbeit |
| dockerhub-username | `false` | Change the Docker Hub username from which the Docker image gets provided. | bytebang |
| dockerhub-repository | `false` | Change the Docker Hub repository name from which the Docker image gets provided. | htlle-da-env |
| manual-mode | `false` | If the repository should not be checked out automatically, specify the complete workspace path to `thesis-path`. | [actions/checkout](https://github.com/actions/checkout) |

### Usage

This section is only relevant if the file `diploma-thesis-action.yml` is used.

Only build:

```yml
- name: Build And Send Diploma Thesis
  uses: HTL-Leoben/da-base-template@main
```

Build and send:

```yml
- name: Build And Send Diploma Thesis
  uses: HTL-Leoben/da-base-template@main
  with:
    mail: ${{ secrets.SENDING_MAIL }}
    mail-password: ${{ secrets.SENDING_MAIL_PASSWORD }}
    smtp-server: ${{ secrets.SMTP_SERVER }}
    smtp-port: ${{ secrets.SMTP_PORT }}
    receiving-mail: ${{ secrets.RECEIVING_MAIL }}
```

Override everything:

```yml
- name: Build And Send Diploma Thesis
  uses: HTL-Leoben/da-base-template@main
  with:
    mail: ${{ secrets.SENDING_MAIL }}
    mail-password: ${{ secrets.SENDING_MAIL_PASSWORD }}
    smtp-server: ${{ secrets.SMTP_SERVER }}
    smtp-port: ${{ secrets.SMTP_PORT }}
    receiving-mail: ${{ secrets.RECEIVING_MAIL }}
    mail-body: git log -1 --pretty=%B
    thesis-path: Diplomarbeit
    dockerhub-username: bytebang
    dockerhub-repository: htlle-da-env
    manual-mode: ${{ github.workspace }}
```

### Secrets

In your GitHub repository you need to [create the secrets](https://docs.github.com/en/actions/security-for-github-actions/security-guides/using-secrets-in-github-actions#creating-secrets-for-a-repository) the Action needs with the information from your corresponding accounts if you want to send an email / message containing the built diploma thesis.

| Name | Usage |
| - | - |
| SENDING_MAIL | The email address from which the diploma thesis should be sent from.  |
| SENDING_MAIL_PASSWORD | The password for the email address corresponding to SENDING_MAIL. |
| SMTP_SERVER | The SMTP server for the email address defined in SENDING_MAIL. |
| SMTP_PORT | The SMTP port corresponding to SMTP_SERVER. |
| RECEIVING_MAIL | The recipient’s email address. If the desired recipient is a Microsoft Teams channel, use its channel email address. |

After creating the secrets it should look like this:

![GitHub build Action secret overview](img/github-build-action-secret-overview.png)

## Notes

- Sending the diploma thesis and thus automated emails using a school email address (Microsoft 365) is not supported. Therefore, use an email address, that does not correspond to your school email address.
- If you use Gmail as a sending email address, you have to generate an [app password](https://support.google.com/accounts/answer/185833) and use this instead of your normal password.
- You can only then see the Microsoft Teams channel email address, if the creator of the team already viewed it once before.

**Author:** [Marko Schrempf](https://github.com/bitsneak)

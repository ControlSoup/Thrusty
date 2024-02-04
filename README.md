# How to Use

Assuming you have the required permissions to access this file. Here is how to clone and run the various projects in this file.

### Generate an ssh key

For a guide on how to generate an ssh key to clone this repo, see ->
[Github ssh keygen](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent)

### Clone the repo

Use the ssh key on this repo and find a nice place in your file structure for it to be stored (Git folder, documents ect)

After you find that, open that path in a terminal.

Once your terminal is open, perform:
```bash
git clone [pasted ssh key form github]
```

### Install requirments and folder as a package

Once the repo is cloned, navigate to its file path, and perform the following command.

```
python3 -m pip install .
```

the "." denotes that you want to install the current folder (with setup.py)
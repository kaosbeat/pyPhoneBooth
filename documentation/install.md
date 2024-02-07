# INSTALLATION

1. RPI64 os
2. install git anmd clone this repo
3. once booted, disable the default rpi audio to have the codeczero as the new default:

```bash
sudo chmod +x audio.sh
sudo ./audio.sh
```


## git install

```
sudo apt install git  
ssh-keygen -t ed25519 -C  "email@com"  
cat /home/pi/.ssh/id_ed25519.pub  
(add it to github)  
```
ssh supports adding a key to the agent on first use (since version 7.2). You can enable that feature by putting the following into ~/.ssh/config:  
AddKeysToAgent yes  
```
vi .ssh/config  

eval "$(ssh-agent -s)"  

ssh-add ~/.ssh/id_ed25519  

git pull  
```
### add deploy key
https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent#generating-a-new-ssh-key

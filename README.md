# bc-thesis

first fast notes from deployment preparation below

to run dev docker container on linux (tested on Ubuntu 20.04 LTS):

sudo chmod 777 media/, include subdirs/files (coz app need to write into media/accounts/..., media/sportdiag/...
folders, its subdirs and files ie. survey attachments or files uploaded by users)
create file project_root_dir/approved_fake_psychologists_raw_passwords.txt
create file project_root_dir/fake_researchers_raw_passwords.txt
set chmod 777 for both files to allow docker container to write into host computer filesystem (probably your PC)
project root in your file system is "shared volume" with running dev docker container (check docker-compose.yml) so only
host user can rw(x) and app also needs to write into some files/dirs (mentioned above) 
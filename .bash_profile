# .bash_profile

# Get the aliases and functions
if [ -f ~/.bashrc ]; then
    source ~/.bashrc
fi

# Load the base environment
home

if [[ $(hostname) == *"login"* ]]
then
    module load Python/3.11.4
else
    base &&
    activate_cur_venv&&
    set_lwd
fi &&

clear &&
qs

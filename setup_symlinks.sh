#!/bin/bash

# Load basic environment variables
cd $PWD
source .bash_env

# Create symlinks for bash configuration files
cd $HOME
ln -s /gpfs/project/$USER_NAME/.usr_tls/.bashrc .bashrc
ln -s /gpfs/project/$USER_NAME/.usr_tls/.bash_env .bash_env
ln -s /gpfs/project/$USER_NAME/.usr_tls/.bash_profile .bash_profile

# Create symlinks for readline tab tools (inputrc)
ln -s /gpfs/project/$USER_NAME/.usr_tls/.inputrc .inputrc

# Create symlinks for git configuration files
ln -s /gpfs/project/$USER_NAME/.usr_tls/.gitconfig .gitconfig

# Create symlinks for ranger configuration files
cd .config
ln -s /gpfs/project/$USER_NAME/.usr_tls/.config/ranger ranger

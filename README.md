## Dependencies
easydict  
tkinter  
ttkbootstrap  
PIL  
smbus  
asyncio  
bleak


## Developers
Update SIMULATION in globals.py to change simulation mode. This will tell the application to use real values from a MPU9255 connected to i2c bus 1

For goodness sakes plz make a branch off of dev, add your changes there, and then merge. DONOT push directly to main or dev. 

And if I catch you using github upload, I will find you. 

## Insutructions Running on pi

```

    #setup virtual environment
    python3 -m venv .env
    source .env/bin/activate
    pip install tkinter bleak smbus asyncio PIL ttkbootstrap tkinter easydict

    cd ~/workspace/
    #if not already cloned
    
    git clone https://github.com/CPompey1/Wayfinder
    cd Wayfinder
    
    #If code is not up to date
    git checkout main
    git pull

    #Assumes virtual environment is already created and initialized with packages in home directory
    cp ~/.env .
    
    #might be in workspace: cp ~/workspace/.env .
    source ./env/bin/activate
    python3 mult_pages.py
    
```

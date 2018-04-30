import requests
import getpass
import helper_functions

def main():
    username = getpass.getuser()
    password = getpass.getpass()

    sess = requests.Session()

    sess.auth = (username, password)

    print("\n[Authorizing]") 
    helper_functions.authorize(sess, username)

    print("\n[Confirming Authorization]") 
    helper_functions.test_auth(sess, username)
    

if __name__ == "__main__":
    main()

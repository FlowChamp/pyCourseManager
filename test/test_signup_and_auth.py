import requests
import getpass
import helper_functions

def main():
    username = getpass.getuser()
    password = getpass.getpass()

    sess = requests.Session()

    sess.auth = (username, password)

    print("[Requesting PIN]")
    token = helper_functions.get_pin(sess, "james.r.heald@gmail.com")
    
    PIN = input("\nPlease enter the received PIN: ")
    
    print("\n[Signing Up]")
    helper_functions.sign_up(sess, token, PIN)

    print("\n[Authenticating, even though Sign Up did as well]") 
    helper_functions.authorize(sess, username) 

    print("\n[Testing Authorization]") 
    helper_functions.test_auth(sess, username)
    

if __name__ == "__main__":
    main()

import requests
import getpass
import helper_functions

def main():
    username = getpass.getuser()
    password = getpass.getpass()

    sess = requests.Session()

    sess.auth = (username, password)

    print("[Requesting PIN]")
    token = get_pin(sess, "james.r.heald@gmail.com")
    
    PIN = input("\nPlease enter the received PIN: ")
    
    print("\n[Signing Up]")
    sign_up(session, token, PIN)

    print("\n[Testing Authorization]") 
    test_auth(username)
    

if __name__ == "__main__":
    main()

import helper_functions

def main():
    sess, username = helper_functions.make_session()

    print("[Requesting PIN]")
    token = helper_functions.get_pin(sess, helper_functions.EMAIL)
    
    PIN = input("\nPlease enter the received PIN: ")
    
    print("\n[Signing Up]")
    helper_functions.sign_up(sess, token, PIN)

    print("\n[Testing Authorization]") 
    helper_functions.test_auth(sess, username)
    

if __name__ == "__main__":
    main()

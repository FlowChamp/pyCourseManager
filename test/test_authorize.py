import helper_functions

def main():
    sess = helper_functions.make_session()

    print("\n[Authorizing]") 
    helper_functions.authorize(sess, username)

    print("\n[Confirming Authorization]") 
    helper_functions.test_auth(sess, username)
    

if __name__ == "__main__":
    main()

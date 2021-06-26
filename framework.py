from WorkQueues import WorkQueues
from Credentials import Credentials
from RPA.Browser.Selenium import Selenium


def main():
    
    # Loader framework
    cred = Credentials()
    username, password = cred.get_credential("YOUR_CRED_NAME")
    # Your code goes here
    #
    data = [
        {
            "field1":"",
            "field2":""
        },
        {
            "field1":"",
            "field2":""
        }       
    ]
    
    WQ = WorkQueues()
    success = WQ.add_to_queue(data,"field1")
    if not success:
        raise Exception("Fail to add data to queue")

    
    # Processor framework
    while True:
        data, item_id = WQ.get_next_item()
        if not data:
            break
        try:
        # Your code goes here
            pass
        #
        except:
            WQ.mark_item_as_exception(item_id, status="item status", Exception_Reason="System Exception: Reason")
        WQ.mark_item_as_completed(item_id, status="item status", tag="item tag")


if __name__ == "__main__":
   main()
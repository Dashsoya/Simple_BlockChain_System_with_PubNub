import json
import hashlib
import time
from pubnub.callbacks import SubscribeCallback
from pubnub.enums import PNStatusCategory
from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub

pnconfig = PNConfiguration()
pnconfig.subscribe_key = 'sub-c-3d36fcf0-ffc0-4980-ab0a-9acd7997c7ff'
pnconfig.publish_key = 'pub-c-d25d03f4-ba7e-492f-b1fb-cd2a3de7ed0a'

def my_publish_callback(envelope, status):
    if not status.is_error():	#to indicate the message sent successfully
        print("Message successfully published to specified channel.")
    else:
        print("Message publish error:", status.error_data)

class MySubscribeCallback(SubscribeCallback):
    def presence(self, pubnub, presence):
        pass

    def status(self, pubnub, status):
        if status.category == PNStatusCategory.PNUnexpectedDisconnectCategory:
            pass
        elif status.category == PNStatusCategory.PNConnectedCategory:
            pass

    def message(self, pubnub, message):
        global can_mine
        print(message.message)	#show the block that was published
        if message.message != "":
            fw = open(str(i) + ".json", "w+") 	#open new file 
            fw.write(message.message)		#save the message inside
            fw.close()
            data = json.loads(message.message)	#get the whole block
            fr = open(str(i - 1) + ".json", "r") #open previous block file
            preblk = fr.read()		#save block to variable preblk
            fr.close()
            if hashlib.sha256(preblk.encode()).hexdigest() == data["Hash"]:
                can_mine = True
                #if hash of preblk is the same as the hash inside the current block then set can_mine flag to True (Verification)

pnconfig.user_id = "Bob"
pubnub = PubNub(pnconfig)
pubnub.add_listener(MySubscribeCallback())
pubnub.subscribe().channels('Channel-Bob').execute()

can_mine = False #because alice will start mining first
transactions = [ "[3, 4, 5, 6]", "[4, 5, 6, 7]", "[5, 6, 7, 8]", "[6, 7, 8, 9]", "[7, 8, 9, 10]", "[8, 9, 10, 11]", "[9, 10, 11, 12]", "[10, 11, 12, 13]", "[11, 12, 13, 14]", "[12, 13, 14, 15]", "[13, 14, 15, 16]"]

def bob_mine():
    global can_mine
    global i
    
    for i in range(len(transactions)+1):

        # Perform mining operations for even blocks
        if i % 2 == 1:		#Bob will mine even blocks
				#so if i is even, it will skip, if i is odd, it enters while loop since block even = transaction [odd]
            #Wait for Alice to send signal
            while can_mine == False :
                time.sleep(1)  # Wait for 1 second before checking again
            
            if i == 11:	#added additional index so bob can save file of 11.json
                exit()    
                
            # Mining logic
            blknum = i + 1
            fr = open(str(blknum - 1) + ".json", "r")
            preblk = fr.read()
            fr.close()
            prehash = hashlib.sha256(preblk.encode()).hexdigest()
            nonce = 1000000000 #bob's nounce start at 1000000000
            cond = True
            while cond:				#block 2 = transaction[1]
                tx = json.dumps({			#transactions[1/3/5]
                    'Block number': blknum, 'Transaction': transactions[i], 'Hash': prehash, 'Nonce': nonce}, sort_keys=True, indent=4,
                    separators=(',', ': '))
                hashcheck = hashlib.sha256(tx.encode()).hexdigest()
                if int(hashcheck, 16) < 2**236:   #assignment criteria
                    cond = False
                nonce = nonce + 1	#nounce increment by 1
                #print(tx)		
            fw = open(str(blknum) + ".json", "w+") #once mined, save block to block_number.json
            fw.write(tx)
            fw.close()
            pubnub.publish().channel("Channel-Alice").message(tx).pn_async(my_publish_callback) #publish so alice can receive
        can_mine = False #set flag to false so it will not start mining again in loop

bob_mine() #running of function


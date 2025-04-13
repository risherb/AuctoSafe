from django.shortcuts import render
from django.template import RequestContext
from django.contrib import messages
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
import os
from Blockchain import *
from Block import *
from datetime import date, datetime
import base64
import numpy as np

import Blockchain
from Blockchain import *

blockchain = Blockchain()
if os.path.exists('blockchain_contract.txt'):
    with open('blockchain_contract.txt', 'rb') as fileinput:
        blockchain = pickle.load(fileinput)
    fileinput.close()

def BidderScreen(request):
    return render(request, 'BidderScreen.html')


private_key, public_key = blockchain.generateDMEKeys()    

def CreateTender(request):
    if request.method == 'GET':
       return render(request, 'CreateTender.html', {})

def splash(request):
    if request.method == 'GET':
       return render(request, 'splash.html', {})

def index(request):
    if request.method == 'GET':
       return render(request, 'index.html', {})
    
def Logout(request):
    if request.method == 'GET':
       return render(request, 'index.html', {})        

def TenderLogin(request):
    if request.method == 'GET':
       return render(request, 'TenderLogin.html', {})

def BidderLogin(request):
    if request.method == 'GET':
       return render(request, 'BidderLogin.html', {})    
    
def Register(request):
    if request.method == 'GET':
       return render(request, 'Register.html', {})

def BidTenderAction(request):
    if request.method == 'GET':
        title = request.GET.get('title', '')
        title = title.strip('"')  # Remove quotes from the title
        print(title+"================")
        
        # Get tender details from blockchain for better display
        tender_details = {}
        for i in range(len(blockchain.chain)):
            if i > 0:
                b = blockchain.chain[i]
                data = b.transactions[0]
                data = str(blockchain.deniableDecrypt(data, private_key))
                data = data[2:len(data)-1]
                arr = data.split("#")
                if arr[0] == "tender" and arr[1] == title:
                    tender_details = {
                        'title': arr[1],
                        'description': arr[2],
                        'open_date': arr[3],
                        'close_date': arr[4],
                        'amount': arr[5]
                    }
                    break
        
        # Create a more structured and informative output with hidden input field
        output = '<table class="table table-bordered">'
        output += '<tr><th style="width: 30%"><font color="white">Tender Title</th><td><input type="text" class="form-control" value="' + title + '" readonly><input type="hidden" name="t1" value="' + title + '"></td></tr>'
        if tender_details:
            output += '<tr><th><font color="white">Description</th><td><font color="white">' + tender_details.get('description', '') + '</td></tr>'
            output += '<tr><th><font color="white">Base Amount</th><td><font color="white">$' + tender_details.get('amount', '') + '</td></tr>'
            output += '<tr><th><font color="white">Open Date</th><td><font color="white">' + tender_details.get('open_date', '') + '</td></tr>'
            output += '<tr><th><font color="white">Close Date</th><td><font color="white">' + tender_details.get('close_date', '') + '</td></tr>'
        output += '</table>'
        
        context = {'data1': output, 'tender_details': tender_details, 'tender_title': title}
        return render(request, 'BidTenderAction.html', context)
        
        
def BidTender(request):
    if request.method == 'GET':
        output = '<table class="table table-bordered table-hover">'
        output += '<thead><tr class="bg-dark">'
        output += '<th><font color="white">Tender Title</th>'
        output += '<th><font color="white">Tender Description</th>'
        output += '<th><font color="white">Open Date</th>'
        output += '<th><font color="white">Close Date</th>'
        output += '<th><font color="white">Base Amount</th>'
        output += '<th><font color="white">Action</th>'
        output += '</tr></thead><tbody>'
        
        # Get current date for comparison
        current_date = datetime.now()
        print(f"Current date: {current_date}")
        
        # Track if we found any open tenders
        found_tenders = False
        
        for i in range(len(blockchain.chain)):
            if i > 0:
                b = blockchain.chain[i]
                data = b.transactions[0]
                data = str(blockchain.deniableDecrypt(data, private_key))
                data = data[2:len(data)-1]
                arr = data.split("#")
                
                # Debug information
                if arr[0] == "tender":
                    print(f"Found tender: {arr[1]}, Open: {arr[3]}, Close: {arr[4]}")
                
                if arr[0] == "tender" and getWinner(arr[1]) == 'none':
                    try:
                        # Try different date formats
                        try:
                            # Try DD-MM-YYYY format
                            open_date_obj = datetime.strptime(arr[3], "%d-%m-%Y")
                            close_date_obj = datetime.strptime(arr[4], "%d-%m-%Y")
                        except ValueError:
                            try:
                                # Try MM/DD/YYYY format
                                open_date_obj = datetime.strptime(arr[3], "%m/%d/%Y")
                                close_date_obj = datetime.strptime(arr[4], "%m/%d/%Y")
                            except ValueError:
                                # Try YYYY-MM-DD format
                                open_date_obj = datetime.strptime(arr[3], "%Y-%m-%d")
                                close_date_obj = datetime.strptime(arr[4], "%Y-%m-%d")
                        
                        # For debugging
                        print(f"Parsed dates - Open: {open_date_obj}, Close: {close_date_obj}")
                        
                        # Always show tenders that are open or will open in the future
                        # Only hide tenders that have closed
                        if current_date <= close_date_obj:
                            found_tenders = True
                            
                            # Truncate description if too long
                            description = arr[2]
                            if len(description) > 50:
                                description = description[:47] + "..."
                            
                            # Format the amount with currency symbol
                            amount = "$" + arr[5]
                            
                            # Calculate days remaining
                            days_remaining = (close_date_obj - current_date).days
                            close_date_display = arr[4]
                            
                            # Show status
                            status = ""
                            if current_date < open_date_obj:
                                status = f" (Opens in {(open_date_obj - current_date).days} days)"
                            elif days_remaining > 0:
                                status = f" ({days_remaining} days remaining)"
                            elif days_remaining == 0:
                                status = " (Closes today)"
                            
                            output += '<tr>'
                            output += '<td><font color="white">' + arr[1] + '</td>'
                            output += '<td><font color="white">' + description + '</td>'
                            output += '<td><font color="white">' + arr[3] + '</td>'
                            output += '<td><font color="white">' + arr[4] + status + '</td>'
                            output += '<td><font color="white">' + amount + '</td>'
                            
                            # Only allow bidding if tender is currently open
                            if current_date >= open_date_obj and current_date <= close_date_obj:
                                output += '<td><a href="BidTenderAction?title=' + arr[1] + '" class="btn btn-primary btn-sm">Place Bid</a></td>'
                            else:
                                output += '<td><button class="btn btn-secondary btn-sm" disabled>Not Open Yet</button></td>'
                            
                            output += '</tr>'
                    except Exception as e:
                        print(f"Error processing tender {arr[1]}: {str(e)}")
        
        output += '</tbody></table>'
        
        if not found_tenders:
            output = '<div class="alert alert-info">No tenders are currently available for bidding. Please check back later.</div>'
        
        context = {'data': output}
        return render(request, 'BidTender.html', context)


def ViewTender(request):
    if request.method == 'GET':
        # Get current user from session
        user = ''
        try:
            with open("session.txt", "r") as file:
                for line in file:
                    user = line.strip('\n')
            file.close()
        except:
            pass
        
        color = '<font color="white">'
        output = '<table class="table table-bordered">'
        output += '<thead><tr class="bg-dark">'
        output += '<th>' + color + 'Tender Title</th>'
        output += '<th>' + color + 'Your Bid Amount</th>'
        output += '<th>' + color + 'Base Amount</th>'
        output += '<th>' + color + 'Submission Date</th>'
        output += '<th>' + color + 'Status</th>'
        output += '</tr></thead><tbody>'
        
        # Track if we found any bids
        found_bids = False
        
        # First collect all tenders to get their details
        tenders = {}
        for i in range(len(blockchain.chain)):
            if i > 0:
                b = blockchain.chain[i]
                data = b.transactions[0]
                #data = base64.b64decode(data)
                data = str(blockchain.deniableDecrypt(data, private_key))
                data = data[2:len(data)-1]
                arr = data.split("#")
                if arr[0] == "tender":
                    tenders[arr[1]] = {
                        'description': arr[2],
                        'open_date': arr[3],
                        'close_date': arr[4],
                        'amount': arr[5]
                    }
        
        # Now collect all bids by this user
        for i in range(len(blockchain.chain)):
            if i > 0:
                b = blockchain.chain[i]
                data = b.transactions[0]
                #data = base64.b64decode(data)
                data = str(blockchain.deniableDecrypt(data, private_key))
                data = data[2:len(data)-1]
                arr = data.split("#")
                if arr[0] == "bidding" and arr[3] == user:
                    found_bids = True
                    tender_title = arr[1]
                    bid_amount = arr[2]
                    status = getWinners(arr[1], arr[3])
                    
                    # Get tender base amount if available
                    base_amount = "N/A"
                    if tender_title in tenders:
                        base_amount = tenders[tender_title]['amount']
                    
                    # Get block timestamp as submission date
                    submission_date = b.timestamp if hasattr(b, 'timestamp') else "N/A"
                    if submission_date != "N/A":
                        try:
                            from datetime import datetime
                            submission_date = datetime.fromtimestamp(int(submission_date)).strftime('%Y-%m-%d %H:%M')
                        except:
                            pass
                    
                    # Format status with color coding
                    status_display = status
                    if status.lower() == "winner":
                        status_display = '<span class="badge bg-success">Winner</span>'
                    elif status.lower() == "pending":
                        status_display = '<span class="badge bg-warning text-dark">Pending</span>'
                    else:
                        status_display = '<span class="badge bg-secondary">Not Selected</span>'
                    
                    output += '<tr>'
                    output += '<td>' + color + tender_title + '</td>'
                    output += '<td>' + color + '$' + bid_amount + '</td>'
                    output += '<td>' + color + '$' + base_amount + '</td>'
                    output += '<td>' + color + str(submission_date) + '</td>'
                    output += '<td>' + status_display + '</td>'
                    output += '</tr>'
        
        output += '</tbody></table>'
        
        if not found_bids:
            output = '<div class="alert alert-info">You have not placed any bids yet. <a href="{% url \'BidTender\' %}" class="alert-link">Click here</a> to view available tenders.</div>'
        
        context = {'data': output}
        return render(request, 'ViewTender.html', context)

def getWinner(title):
    output = 'none'
    for i in range(len(blockchain.chain)):
        if i > 0:
            b = blockchain.chain[i]
            data = b.transactions[0]
            #data = base64.b64decode(data)
            data = str(blockchain.deniableDecrypt(data, private_key))
            data = data[2:len(data)-1]
            print(data)
            arr = data.split("#")
            if arr[0] == "winner" and arr[1] == title:
                output = title
                break
    return output

def getWinners(title, bidder):
    output = 'Lost'
    for i in range(len(blockchain.chain)):
        if i > 0:
            b = blockchain.chain[i]
            data = b.transactions[0]
            #data = base64.b64decode(data)
            data = str(blockchain.deniableDecrypt(data, private_key))
            data = data[2:len(data)-1]
            arr = data.split("#")
            if arr[0] == "winner" and arr[1] == title and arr[4] == bidder:
                output = "Winner"
                break
    return output

def EvaluateTender(request):
    if request.method == 'GET':
        # Create a more modern table
        output = '<table class="table table-bordered table-hover">'
        output += '<thead><tr class="bg-dark">'
        output += '<th><font color="white">Tender Title</th>'
        output += '<th><font color="white">Description</th>'
        output += '<th><font color="white">Number of Bids</th>'
        output += '<th><font color="white">Lowest Bid</th>'
        output += '<th><font color="white">Action</th>'
        output += '</tr></thead><tbody>'
        
        # Get all tenders that have bids but no winner yet
        tenders_with_bids = {}
        
        # First, collect all tenders
        all_tenders = {}
        for i in range(len(blockchain.chain)):
            if i > 0:
                b = blockchain.chain[i]
                data = b.transactions[0]
                data = str(blockchain.deniableDecrypt(data, private_key))
                data = data[2:len(data)-1]
                arr = data.split("#")
                if arr[0] == "tender":
                    all_tenders[arr[1]] = {
                        'description': arr[2],
                        'open_date': arr[3],
                        'close_date': arr[4],
                        'amount': arr[5]
                    }
        
        # Then collect all bids
        for i in range(len(blockchain.chain)):
            if i > 0:
                b = blockchain.chain[i]
                data = b.transactions[0]
                data = str(blockchain.deniableDecrypt(data, private_key))
                data = data[2:len(data)-1]
                arr = data.split("#")
                if arr[0] == "bidding" and arr[4] == "Pending":
                    tender_title = arr[1]
                    bid_amount = float(arr[2])
                    bidder = arr[3]
                    
                    # Skip if tender already has a winner
                    if getWinner(tender_title) != 'none':
                        continue
                        
                    # Initialize if first bid for this tender
                    if tender_title not in tenders_with_bids:
                        tenders_with_bids[tender_title] = {
                            'bids': [],
                            'lowest_bid': float('inf'),
                            'lowest_bidder': None
                        }
                    
                    # Add this bid
                    tenders_with_bids[tender_title]['bids'].append({
                        'amount': bid_amount,
                        'bidder': bidder
                    })
                    
                    # Update lowest bid if applicable
                    if bid_amount < tenders_with_bids[tender_title]['lowest_bid']:
                        tenders_with_bids[tender_title]['lowest_bid'] = bid_amount
                        tenders_with_bids[tender_title]['lowest_bidder'] = bidder
        
        # Now build the table
        if tenders_with_bids:
            for title, info in tenders_with_bids.items():
                description = all_tenders.get(title, {}).get('description', 'N/A')
                if len(description) > 50:
                    description = description[:47] + "..."
                
                num_bids = len(info['bids'])
                lowest_bid = f"${info['lowest_bid']:.2f} ({info['lowest_bidder']})"
                
                output += '<tr>'
                output += f'<td><font color="white">{title}</td>'
                output += f'<td><font color="white">{description}</td>'
                output += f'<td><font color="white">{num_bids}</td>'
                output += f'<td><font color="white">{lowest_bid}</td>'
                output += f'<td><a href="javascript:void(0)" onclick="evaluateTender(\'{title.replace("\'", "\\\'")}\');" class="btn btn-success btn-sm">Select Winner</a></td>'
                output += '</tr>'
        
        output += '</tbody></table>'
        
        if not tenders_with_bids:
            output = '<div class="alert alert-info">No tenders are currently available for evaluation or all tenders have already been evaluated.</div>'
        
        # Add JavaScript function to handle winner selection
        output += '''
        <script>
        function evaluateTender(title) {
            if (confirm("Are you sure you want to select the lowest bidder as the winner for tender '" + title + "'?")) {
                window.location.href = "EvaluateTenderAction?title=" + encodeURIComponent(title);
            }
        }
        </script>
        '''
        
        context = {'data': output}
        return render(request, 'EvaluateTender.html', context)
    
def EvaluateTenderAction(request):
    if request.method == 'GET':
        tender_title = request.GET.get('title', '')
        
        if not tender_title:
            context = {'data': 'Error: No tender title provided'}
            return render(request, 'EvaluateTender.html', context)
        
        # Find the lowest bid for this tender
        lowest_bid = float('inf')
        lowest_bidder = None
        bid_amount = 0
        
        for i in range(len(blockchain.chain)):
            if i > 0:
                b = blockchain.chain[i]
                data = b.transactions[0]
                data = str(blockchain.deniableDecrypt(data, private_key))
                data = data[2:len(data)-1]
                arr = data.split("#")
                if arr[0] == "bidding" and arr[4] == "Pending" and arr[1] == tender_title:
                    current_bid = float(arr[2])
                    if current_bid < lowest_bid:
                        lowest_bid = current_bid
                        lowest_bidder = arr[3]
                        bid_amount = arr[2]
        
        if lowest_bidder:
            # Create winner record in blockchain
            data = "winner#" + tender_title + "#" + str(bid_amount) + "#" + lowest_bidder + "#" + lowest_bidder
            enc = blockchain.deniableEncrypt(data, public_key)
            blockchain.add_new_transaction(enc)
            hash_result = blockchain.mine()
            blockchain.save_object(blockchain, 'blockchain_contract.txt')
            
            context = {'data': f'Winner selected for tender "{tender_title}": {lowest_bidder} with bid amount ${lowest_bid:.2f}'}
        else:
            context = {'data': f'No eligible bids found for tender "{tender_title}"'}
        
        return render(request, 'EvaluateTender.html', context)

def WinnerSelection(request):
    if request.method == 'GET':
        # Create a more modern table
        output = '<table class="table table-bordered table-hover">'
        output += '<thead><tr class="bg-dark">'
        output += '<th><font color="white">Tender Title</th>'
        output += '<th><font color="white">Description</th>'
        output += '<th><font color="white">Winner</th>'
        output += '<th><font color="white">Winning Bid</th>'
        output += '<th><font color="white">Base Amount</th>'
        output += '<th><font color="white">Savings</th>'
        output += '</tr></thead><tbody>'
        
        # Track if we found any winners
        found_winners = False
        
        # First collect all tenders
        all_tenders = {}
        for i in range(len(blockchain.chain)):
            if i > 0:
                b = blockchain.chain[i]
                data = b.transactions[0]
                data = str(blockchain.deniableDecrypt(data, private_key))
                data = data[2:len(data)-1]
                arr = data.split("#")
                if arr[0] == "tender":
                    all_tenders[arr[1]] = {
                        'description': arr[2],
                        'open_date': arr[3],
                        'close_date': arr[4],
                        'amount': float(arr[5])
                    }
        
        # Then collect all winners
        winners = {}
        for i in range(len(blockchain.chain)):
            if i > 0:
                b = blockchain.chain[i]
                data = b.transactions[0]
                data = str(blockchain.deniableDecrypt(data, private_key))
                data = data[2:len(data)-1]
                arr = data.split("#")
                if arr[0] == "winner":
                    found_winners = True
                    tender_title = arr[1]
                    bid_amount = float(arr[2])
                    bidder = arr[3]
                    
                    winners[tender_title] = {
                        'bidder': bidder,
                        'amount': bid_amount
                    }
        
        # Now build the table
        if found_winners:
            for title, info in winners.items():
                tender_info = all_tenders.get(title, {})
                description = tender_info.get('description', 'N/A')
                if len(description) > 50:
                    description = description[:47] + "..."
                
                base_amount = tender_info.get('amount', 0)
                savings = base_amount - info['amount']
                savings_percent = (savings / base_amount * 100) if base_amount > 0 else 0
                
                output += '<tr>'
                output += f'<td><font color="white">{title}</td>'
                output += f'<td><font color="white">{description}</td>'
                output += f'<td><font color="white">{info["bidder"]}</td>'
                output += f'<td><font color="white">${info["amount"]:.2f}</td>'
                output += f'<td><font color="white">${base_amount:.2f}</td>'
                
                if savings > 0:
                    output += f'<td><font color="green">${savings:.2f} ({savings_percent:.1f}%)</td>'
                else:
                    output += f'<td><font color="red">No savings</td>'
                
                output += '</tr>'
        
        output += '</tbody></table>'
        
        if not found_winners:
            output = '<div class="alert alert-info">No winners have been selected yet. Please evaluate tenders first.</div>'
        
        context = {'data': output}
        return render(request, 'WinnerSelection.html', context)

def BidTenderActionPage(request):
    if request.method == 'POST':
        # Debug information
        print("POST data received:", request.POST)
        
        # Get form data with proper default values
        title = request.POST.get('t1', '')
        amt = request.POST.get('t2', '')
        
        # Debug the values
        print(f"Title: '{title}', Amount: '{amt}'")
        
        # Validate the inputs
        if not title or not amt:
            context = {'data': f'Error: Missing tender title or bid amount. Title: {title}, Amount: {amt}'}
            return render(request, 'BidderScreen.html', context)
        
        try:
            # Convert amount to float to ensure it's a valid number
            float_amt = float(amt)
            if float_amt <= 0:
                context = {'data': 'Error: Bid amount must be greater than zero'}
                return render(request, 'BidderScreen.html', context)
            
            # Get current user from session
            user = ''
            try:
                with open("session.txt", "r") as file:
                    for line in file:
                        user = line.strip('\n')
                file.close()
                
                if not user:
                    context = {'data': 'Error: User session not found. Please log in again.'}
                    return render(request, 'BidderLogin.html', context)
            except Exception as e:
                context = {'data': f'Error accessing session: {str(e)}'}
                return render(request, 'BidderLogin.html', context)
            
            # Create the bid data
            data = "bidding#" + str(title) + "#" + str(amt) + "#" + str(user) + "#Pending"
            
            # Encrypt and store in blockchain
            enc = blockchain.deniableEncrypt(str(data), public_key)
            blockchain.add_new_transaction(enc)
            hash_result = blockchain.mine()
            
            # Get the latest block
            b = blockchain.chain[len(blockchain.chain)-1]
            
            # Format the blockchain information
            bc = f"Previous Hash: {b.previous_hash}<br/>Block No: {b.index}<br/>Current Hash: {b.hash}"
            
            # Save the updated blockchain
            blockchain.save_object(blockchain, 'blockchain_contract.txt')
            
            # Return success message
            context = {
                'data': f'<div class="alert alert-success">Your bid of ${amt} for tender "{title}" was submitted successfully!</div><div class="mt-3 small text-muted">Blockchain details:<br/>{bc}</div>'
            }
            return render(request, 'BidderScreen.html', context)
            
        except Exception as e:
            context = {'data': f'Error processing bid: {str(e)}'}
            return render(request, 'BidderScreen.html', context)
        

def CreateTenderAction(request):
    if request.method == 'POST':
        title = request.POST.get('t1', False)
        description = request.POST.get('t2', False)
        open_date = request.POST.get('t3', False)
        close_date = request.POST.get('t4', False)
        amt = request.POST.get('t5', False)
        data = "tender#"+title+"#"+description+"#"+open_date+"#"+close_date+"#"+amt
        enc = blockchain.deniableEncrypt(str(data), public_key)
        #enc = str(base64.b64encode(enc),'utf-8')
        blockchain.add_new_transaction(enc)
        hash = blockchain.mine()
        b = blockchain.chain[len(blockchain.chain)-1]
        print("Previous Chamelion Hash : "+str(b.previous_hash)+" Block No : "+str(b.index)+" Current Chamelion Hash : "+str(b.hash))
        bc = "Previous Chamelion Hash : "+str(b.previous_hash)+"<br/>Block No : "+str(b.index)+"<br/>Current Chamelion Hash : "+str(b.hash)+"<br/>Encrypted Data : "+str(enc)
        blockchain.save_object(blockchain,'blockchain_contract.txt')
        context= {'data':'Tender Created Successfully.<br/>'+bc}
        return render(request, 'CreateTender.html', context)
        

def Signup(request):
    if request.method == 'POST':
        username = request.POST.get('username', False)
        password = request.POST.get('password', False)
        contact = request.POST.get('contact', False)
        email = request.POST.get('email', False)
        cname = request.POST.get('cname', False)
        address = request.POST.get('address', False)
        check = checkUser(username)
        if check == 'none':
            data = "signup#"+username+"#"+password+"#"+contact+"#"+email+"#"+cname+"#"+address
            enc = blockchain.deniableEncrypt(str(data), public_key)
            #enc = str(base64.b64encode(enc),'utf-8')
            blockchain.add_new_transaction(enc)
            hash = blockchain.mine()
            b = blockchain.chain[len(blockchain.chain)-1]
            print("Previous Chamelion  Hash : "+str(b.previous_hash)+" Block No : "+str(b.index)+" Current Chamelion  Hash : "+str(b.hash))
            bc = "Previous Chamelion  Hash : "+str(b.previous_hash)+"<br/>Block No : "+str(b.index)+"<br/>Current Chamelion  Hash : "+str(b.hash)
            blockchain.save_object(blockchain,'blockchain_contract.txt')
            context= {'data':'Signup process completd and record saved in Blockchain with below hashcodes.<br/>'+bc}
            return render(request, 'Register.html', context)
        else:
            context= {'data':'Username already exists'}
            return render(request, 'Register.html', context)


def TenderLoginAction(request):
    if request.method == 'POST':
        username = request.POST.get('username', False)
        password = request.POST.get('password', False)
        if username == 'admin' and password == 'admin':
            context= {'data':'Welcome '+username}
            return render(request, 'TenderScreen.html', context)
        else:
            context= {'data':'Invalid Login'}
            return render(request, 'TenderLogin.html', context)
            


def BidderLoginAction(request):
    if request.method == 'POST':
        username = request.POST.get('username', False)
        password = request.POST.get('password', False)
        status = 'none'
        for i in range(len(blockchain.chain)):
            if i > 0:
                b = blockchain.chain[i]
                data = b.transactions[0]
                #data = base64.b64decode(data)
                data = str(blockchain.deniableDecrypt(data, private_key))
                data = data[2:len(data)-1]
                arr = data.split("#")
                if arr[0] == "signup":
                    if arr[1] == username and arr[2] == password:
                        status = 'success'
                        break
        if status == 'success':
            file = open('session.txt','w')
            file.write(username)
            file.close()
            context= {'data':"Welcome "+username}
            return render(request, 'BidderScreen.html', context)
        else:
            context= {'data':'Invalid login details'}
            return render(request, 'BidderLogin.html', context)
        
        

def TenderScreen(request):
    if request.method == 'GET':
        # Count total tenders
        total_tenders = 0
        # Count total bids
        total_bids = 0
        # Count pending evaluations
        pending_evaluations = 0
        
        for i in range(len(blockchain.chain)):
            if i > 0:
                b = blockchain.chain[i]
                data = b.transactions[0]
                data = str(blockchain.deniableDecrypt(data, private_key))
                data = data[2:len(data)-1]
                arr = data.split("#")
                if arr[0] == "tender":
                    total_tenders += 1
                elif arr[0] == "bidding":
                    total_bids += 1
                    if arr[4] == "Pending":
                        pending_evaluations += 1
        
        context = {
            'data': 'Welcome to the Tender Officer Dashboard',
            'total_tenders': total_tenders,
            'total_bids': total_bids,
            'pending_evaluations': pending_evaluations
        }
        return render(request, 'TenderScreen.html', context)

def checkUser(username):
    output = 'none'
    for i in range(len(blockchain.chain)):
        if i > 0:
            b = blockchain.chain[i]
            data = b.transactions[0]
            #data = base64.b64decode(data)
            data = str(blockchain.deniableDecrypt(data, private_key))
            data = data[2:len(data)-1]
            print(str(data)+"#######")
            arr = data.split("#")
            if arr[0] == "signup":
                if arr[1] == username:
                    output = "exists"
                    break
    return output

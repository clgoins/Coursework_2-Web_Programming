document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);

  document.querySelector('#compose-form').addEventListener('submit', sendEmail);

  // By default, load the inbox
  load_mailbox('inbox');
});


function compose_email() {

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out the values for the three text fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
  
}


function load_mailbox(mailbox) {
  
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;


  // Get the contents of the mailbox from the server
  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {
    console.log(emails);

    // Iterate through each email returned, generate a 'mail card', and append that card to the emails-view div.
    emails.forEach(function (email){
      let card = generateMailCard(email, mailbox);
      document.querySelector('#emails-view').append(card);
    })
  })

}


function sendEmail() {

    // Makes a post request to the email API containing all the form data the user entered from the compose page
    fetch("/emails", {
      method: "POST",
      body: JSON.stringify({
        recipients: document.querySelector('#compose-recipients').value,
        subject: document.querySelector('#compose-subject').value,
        body: document.querySelector('#compose-body').value
      })
    })
    .then(response => response.json())
    .then(result => {
      //print the servers respone to the console and load up the 'sent' mailbox.
      console.log(result);
      load_mailbox('sent');
    })

    //return false to prevent from accidentally submitting the form anywhere
    return false;
}


function generateMailCard(email, mailbox) {
  
  // The card will be a div element with a class of 'emailRead' or 'emailUnread' depending on whether the email has been read yet.
  let card = document.createElement('div');
  
  if(email.read === true)
    card.className = 'emailRead';
  else
    card.className = 'emailUnread';

  // Create a table element with the class of 'emailContent' to lay all the necessary infomation out in the card div.  
  let content = document.createElement('table');
  content.className = 'emailContent'

  // Create 3 data cells each with part of the information to display in the card.
  let sender = `<td class='senderData'>${email.sender}</td>`;
  let subject = `<td class='subjectData'>${email.subject}</td>`;
  let timestamp = `<td class='timestampData'>${email.timestamp}</td>`

  // Add the data cells to the innerHTML of the table
  content.innerHTML = sender + subject + timestamp;

  // Populate the card with the content table that was just created
  card.append(content);

  // Add an event listener to the card to run the loadEmail function whenever the card is clicked
  card.addEventListener('click', () => loadEmail(email, mailbox));

  // Return the card to add it to the document
  return card;
}


//loads the full contents of a single email
function loadEmail(email, mailbox)
{
  let emailView = document.querySelector('#email-view');

  // Show single email view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';
  emailView.style.display = 'block';

  // Send request to server to update the emails status to 'read'
  fetch(`/emails/${email.id}`, {
    method:'PUT', 
    body: JSON.stringify({
      read: true
    })
  })
  .then(response => console.log(response));

  // Clear the contents of email-view
  emailView.innerHTML = '';

  // Display the contents of the email

  // Create a div for the metadata to display (sender, recipients, timestamp) and add that data to it
  let metaDiv = document.createElement('div');
  metaDiv.innerHTML = `<div>To: <span style="color:blue">${email.recipients}</span></div>`;
  metaDiv.innerHTML += `<div>From: <span style="color:blue">${email.sender}</span></div>`;
  metaDiv.innerHTML += `<p>${email.timestamp}</p>`;

  // Create a div for the subject line and add the subject text to it
  let subDiv = document.createElement('div');
  subDiv.className = 'subjectField';
  subDiv.innerHTML += `<h3>${email.subject}</h3>`;

  // Create a div for the body of the email and add the body data to it
  let bodyDiv = document.createElement('div');
  bodyDiv.className = 'bodyField';
  //make sure the 'white-space: pre-wrap' style is set to preserve line breaks in the original email
  bodyDiv.innerHTML += `<p style="white-space: pre-wrap;">${email.body}</p>`;

  // Append all 3 divs to the emailView section of the page
  emailView.append(metaDiv);
  emailView.append(subDiv);
  emailView.append(bodyDiv);

  // Check which mailbox this email is in. if it's the inbox, add an 'archive' and 'reply' button. If it's the archive, add an 'unarchive' button. If it's the sent messages, add no buttons.
  if(mailbox === 'inbox')
  {
    emailView.append(createEmailButtons('archive', email));
    emailView.append(createEmailButtons('reply', email));
  }
  else if (mailbox === 'archive')
  {
    emailView.append(createEmailButtons('unarchive', email));
  }

}


// Factored out code for creating the buttons that display when viewing an email
function createEmailButtons(buttonType, email)
{

    //create a generic button and add some style properties
    let button = document.createElement('button');
    button.style.marginTop = '10px';
    button.style.marginRight = '10px';

    //based on the type of button requested (archive, unarchive, or reply), set its innerHTML and give it an eventListener
    if (buttonType === 'archive')
    {
      button.innerHTML = 'Archive';

      //make a PUT request to the server to update the emails archive status to true, then load the inbox
      button.addEventListener('click', () => {
        fetch(`/emails/${email.id}`,{
          method:'PUT',
          body: JSON.stringify({
              archived:true
          })
        })
        .then(response => {
          load_mailbox('inbox');
          console.log(response);
        });
      })
    }

    else if (buttonType === 'unarchive')
    {
        button.innerHTML = 'Unarchive';

        //make a PUT request to the server to update the emails archive status to false, then load the inbox
        button.addEventListener('click', () => {
          fetch(`/emails/${email.id}`,{
            method:'PUT',
            body: JSON.stringify({
                archived:false
            })
          })
          .then(response => {
            load_mailbox('inbox');
            console.log(response);
          });
        })
    }

    else if (buttonType === 'reply')
    {
        button.innerHTML = 'Reply';

        //call the 'reply' function, and provide the information that needs to be pre-filled in the composition forms
        button.addEventListener('click', () => reply(email));
    }

    return button;
}


// Very similar to compose_email, but accepts some arguments used to pre-fill the forms when replying to another email
function reply(email) {

  console.log("running reply function");

  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#email-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Set the default values for the three fields (empty strings for a new composition, or pre-filled if this is a reply to another email)
  document.querySelector('#compose-recipients').value = email.sender;

  // Add 'Re: ' to the subject line if it isn't there already
  if(email.subject.substring(0,4) == 'Re: ')
    document.querySelector('#compose-subject').value = email.subject;
  else
    document.querySelector('#compose-subject').value = `Re: ${email.subject}`;

  // Add the time stamp and original sender to the body of the original email
  document.querySelector('#compose-body').value = `\n\nAt ${email.timestamp}; ${email.sender} wrote: ${email.body}`;

}

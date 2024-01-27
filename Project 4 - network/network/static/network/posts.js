
const csrftoken = document.querySelector('[name=csrfmiddlewaretoken]').value;
updateLikeCounts()

document.querySelectorAll("[name=like_link]").forEach(element => {
    element.addEventListener('click', likeUnlike);
})

document.querySelectorAll("[name=edit_link]").forEach(element => {
    element.addEventListener('click', editPost);
})

//event listener for the 'like_link' elements
//sends the postID off to the server to create or destroy a 'like' entry in the database
function likeUnlike()
{
    postID = this.dataset.id;
    fetch("/like", {
        method:'POST',
        headers: {'X-CSRFToken':csrftoken},
        mode: 'same-origin',
        body: JSON.stringify({
            id:postID
        })
    })
    .then((response) => response.json())
    .then((result) => {
        console.log(result);
        refreshPost(postID);
    })

    return false;
}


//updates the like counts for every post visible on the page
function updateLikeCounts()
{
    //create a list of all the posts currently shown on the page
    let IDs = [];
    document.querySelectorAll("[name=like_count]").forEach(element => {
        IDs.push(element.dataset.id);
    });

    //send the list to the 'likeCount' route via POST request
    fetch("/likeCount", {
        method:'POST',
        headers: {'X-CSRFToken':csrftoken},
        mode: 'same-origin',
        body: JSON.stringify({
                postIDs:IDs
        })
    })
    .then((response) => response.json())
    .then((result) => {
        // server will return an array of objects
        // keys are id=, likeCount=, liked=
        for (let i = 0; i < result.length; i++)
        {
            document.querySelector(`#like_count_${result[i]["id"]}`).innerHTML = result[i]["likeCount"];

            if(result[i]["liked"])
                document.querySelector(`#like_link_${result[i]["id"]}`).innerHTML = "Unlike";
            else
                document.querySelector(`#like_link_${result[i]["id"]}`).innerHTML = "Like";
        }
    });
}


//allows a user to edit their own posts
function editPost()
{
    let postID = this.dataset.id;
    let originalText = document.querySelector(`#post_body_${postID}`).innerHTML;

    document.querySelector(`#edit_link_${postID}`).innerHTML = "";
    document.querySelector(`#post_body_${postID}`).innerHTML = 
        `<textarea id="post_edit_${postID}" style='outline:none; border:none; width:99%; resize:none' maxlength=500>${originalText}</textarea>
        <br>
        <a href="#a" onclick="submitEdit(${postID})">Submit</a>
        <a href="#a" onclick="refreshPost(${postID})" style='margin-left:15px'>Cancel</a>`
}

function submitEdit(postID)
{
    editText = document.querySelector(`#post_edit_${postID}`).value;

    fetch("/post", {
        method:'POST',
        headers: {'X-CSRFToken':csrftoken},
        mode: 'same-origin',
        body: JSON.stringify({
                id:postID,
                body:editText
        })
    })
    .then((response) => response.json())
    .then((result) => {
        console.log(result);
        refreshPost(postID);
    })
}

//updates the information in a single post without having to reload the whole page
//should be called at the end of editPost() and likeUnlike()
function refreshPost(postID)
{
    fetch("/post" + `?id=${postID}`)
    .then((response) => response.json())
    .then((result) => {
        document.querySelector(`#post_body_${postID}`).innerHTML = result['body'];
        document.querySelector(`#like_count_${postID}`).innerHTML = result['likeCount'];
        
        //if a post edit is cancelled, this link will need to be replaced
        if(document.querySelector(`#edit_link_${postID}`))
            document.querySelector(`#edit_link_${postID}`).innerHTML = "Edit Post"

        if(result['liked'])
            document.querySelector(`#like_link_${postID}`).innerHTML = "Unlike";
        else
        document.querySelector(`#like_link_${postID}`).innerHTML = "Like";

    })
}

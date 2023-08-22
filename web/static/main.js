console.log("sejm info")

function onLinkClicked(readItemId) {
     let cookieAccepted=Cookies.get('cookiesAccepted')
     if (cookieAccepted==0){
        return;
     }
    let readItems = Cookies.get('readItems');
    if(readItems != undefined && readItems != 'undefined'){
        if (!readItems.includes(readItemId)) {
            readItems+=`,${readItemId}`
        }
    }
    else{
        readItems=readItemId
    }
   

    Cookies.set('readItems', readItems, { expires: 365 })
}

function markAlreadyReadLinks() {
    let readItems = Cookies.get('readItems');
    if(readItems != undefined && readItems != 'undefined'){
        readItems=readItems.split(",")

    for (let alreadyReadItem of readItems) {
        document.getElementById(alreadyReadItem).style.color = "#a669b9";
    }
     }
}
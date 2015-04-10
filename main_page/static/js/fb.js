function timeIsPast(time){
    currentTime = new Date($.now());
    return (currentTime > time);
}
function processEvent(i){
}
function generateEvent(i, f){
    d = $.data(document, "events").data[i];
    FB.api("/" + d.id, function(response){
        $.data(document, "description", response);
        //%TODO: Description
        //%TODO: Cover photo
    });
    return "<div class=\"event block\">"
        + "<a href=\"https://www.facebook.com/events/" + d.id + "\">"
        + "<div class=\"event-name\">" + d.name + "</div>"
        + "</a>"
//        + "<div class=\"event-photo\">"
//        + "<img src=\"" + d.image + ">"
//        + "</div>"
        + "<div class=\"event-timelocation\">"+ new Date(d.start_time).toString() 
        + ", " + d.location + "</div>"
//        + "<div class=\"text\">"
//        + $.data(document, "description") + "</div></div>";
}
window.fbAsyncInit = function() {
    FB.init({
        appId      : '1491550594450453',
        xfbml      : true,
        cookie     : true,
        version    : 'v2.1'
    });
    FB.getLoginStatus(function(response){
        if(!response.authResponse){
            FB.login(function(response){}
        , {scope: 'user_groups'})
        }
        FB.api("/2200089855/events", function(response){
            if(response && !response.error){
                $.data(document, "events", response);
                var i = 0;
                while(!timeIsPast(new Date($.data(document, "events").data[i].start_time))){
                    i++;
                }
                $.data(document, "index", i);
                if($.data(document, "index") === 0){
                    $(".columnleft").append("No new events for now! Check back soon.");
                }
                for(i = $.data(document, "index") - 1; i >= 0 ; i--){
                    $(".columnleft").append(generateEvent(i, processEvent));
                };
                for(i = 2; i >= 0; i--){
                    var j = i + $.data(document, "index");
                    $(".columnright").append(generateEvent(j, processEvent));
                }
            };
        });
    });
}; 
(function(d, s, id){
    var js, fjs = d.getElementsByTagName(s)[0];
    if (d.getElementById(id)) {return;}
    js = d.createElement(s); js.id = id;
    js.src = "//connect.facebook.net/en_US/sdk.js";
    fjs.parentNode.insertBefore(js, fjs);
}(document, 'script', 'facebook-jssdk'));


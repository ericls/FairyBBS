$(document).ready(function(){
    $('.reply-btn').click(
        function(){
           var user=$(this).data('user');
           console.log(user);
           $('#content').append('@' + user + ' '); 
        }
    );
});

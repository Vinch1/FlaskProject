function bindEmailCaptchaClick(){
    // 整个网页都加载完毕后执行
    $(function (){
        $("#captcha-btn").click(function (e){

            var $this = $(this);
            //阻止默认的事件
            e.preventDefault();

            var email = $("#email").val();
            $.ajax({
                url: "/auth/captcha/email?email="+email,
                method: "GET",
                success: function (result){
                    var code = result['code'];
                    if (code == 200){
                        var countdown = 60;
                        //取消点击事件
                        $this.off("click");
                        var timer = setInterval(function (){
                            $this.text(countdown);
                            countdown -= 1;
                            if (countdown <= 0){
                                //清除定时器
                                clearInterval(timer);
                                $this.text("获取验证码");
                                //重新绑定点击事件
                                bindEmailCaptchaClick()
                            }
                        },1000);
                        alert("邮箱验证码发送成功");
                    }else{
                        alert(result['message']);
                    }
                },
                fail: function (error){
                    console.log(error);
                }
            })

        });
    })
}

$(function (){
    bindEmailCaptchaClick();
})
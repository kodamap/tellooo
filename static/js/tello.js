$(function () {
    var stream_cmd = ['streamon', 'streamoff'];
    var info_cmd = ['battery?', 'speed?', 'temp?'];
    var tracking_cmd = ['streamonly', 'test', 'tracking'];
    var connect_cmd = ['command'];
    var control_cmd = ['takeoff', 'land', 'up', 'down', 'left', 'right', 'forward', 'back', 'cw', 'ccw', "flip"];
    var info_flg = 0;
    var url = "";
    $(function () {
        // info_flg is used for getting  information correctly of tello per certain interval.
        // i don't think this is smart way..
        setInterval(function () {
            if (info_flg == 1) {
                post('/info', JSON.stringify({ "command": "battery?" }));
            } else if (info_flg == 2) {
                post('/info', JSON.stringify({ "command": "speed?" }));
            } else if (info_flg == 3) {
                post('/info', JSON.stringify({ "command": "temp?" }));
                info_flg = 0;
            }
            info_flg++;
        }, 5000);
    });
    $(function () {
        var n = 20;
        var speed_range = 20;
        $('#qty').val(n);
        $('.plus').on('click', function () {
            if (n < 100) {
                $('#qty').val(n = n + speed_range);
                command = JSON.stringify({ "command": "speed " + n });
                post('/tellooo', command);
            }
        });
        $('.min').on('click', function () {
            if (n > 20) {
                $('#qty').val(n = n - speed_range);
                command = JSON.stringify({ "command": "speed " + n });
                post('/tellooo', command);
            }
        });
    });
    $('.btn').on('click', function () {
        var command = JSON.stringify({ "command": $('#' + $(this).attr('id')).val() });
        if (JSON.parse(command).command == "") {
            var command = JSON.stringify({ "command": $(this).find('input').val() });
        }
        if (info_cmd.includes(JSON.parse(command).command)) {
            url = '/info';
        } else if (connect_cmd.includes(JSON.parse(command).command)) {
            url = '/tellooo';
        } else if (control_cmd.includes(JSON.parse(command).command) || JSON.parse(command).command.match(/flip [l,r,f,b]/)) {
            url = '/tellooo';
        } else if (stream_cmd.includes(JSON.parse(command).command)) {
            url = '/tellooo';
        } else if (tracking_cmd.includes(JSON.parse(command).command)) {
            url = '/tracking';
        }
        post(url, command);
    });
    function post(url, command) {
        $.ajax({
            type: 'POST',
            url: url,
            data: command,
            contentType: 'application/json',
            timeout: 10000
        }).done(function (data) {
            var sent_cmd = JSON.parse(command).command;
            var tello_res = JSON.parse(data.ResultSet).result;
            var connected = JSON.parse(data.ResultSet).connected;
            var streamon = JSON.parse(data.ResultSet).streamon;
            //console.log(JSON.parse(data.ResultSet));
            if (connected) {
                if (connect_cmd.includes(sent_cmd)) {
                    $("#res").text(sent_cmd + ":" + tello_res);
                    if (!streamon) {
                        $('.img-fluid').attr('src', '../../static/images/tello_c.png');
                        $("#command").attr('class', 'btn btn-success');
                        $("#res").text('Click streamon!');
                    }
                }
                if (sent_cmd == "battery?") {
                    $("#battery").text(sent_cmd + ":" + tello_res);
                }
                if (sent_cmd == "speed?" || sent_cmd.match(/speed \d+/)) {
                    sent_cmd = sent_cmd.split(" ", 1)[0]
                    $("#speed").text(sent_cmd + ":" + tello_res);
                }
                if (sent_cmd == "temp?") {
                    $("#temp").text(sent_cmd + ":" + tello_res);
                }
                if (control_cmd.includes(sent_cmd) || tracking_cmd.includes(sent_cmd) || sent_cmd.match(/flip [l,r,f,b]/)) {
                    $("#res").text(sent_cmd + ":" + tello_res);
                }
                if (stream_cmd.includes(sent_cmd)) {
                    $("#res").text(sent_cmd + ":" + tello_res);
                    $(function () {
                        setTimeout(function () {
                            window.location.href = window.location.href
                        }, 1000);
                    });
                }
            } else {
                $("#res").text('Click connect at first!');
            }
        }).fail(function (jqXHR, textStatus, errorThrown) {
            $("#res").text(textStatus + ":" + jqXHR.status + " " + errorThrown);
        });
        return false;
    }
    $(function () {
        $('[data-toggle="tooltip"]').tooltip()
    });
});


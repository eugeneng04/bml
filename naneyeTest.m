function naneyeTest()
    server = tcpserver("127.0.0.1",8888, "Timeout", 30);
    %flush(server);
    naneye = naneyeConstruct();
    disp("waiting for connection");
    while ~server.Connected
        pause(0.1);
    end
    disp("client connected");
    while true
        try
            output = outputdata(naneye);
            %disp(output);
            write(server, output);
            disp(size(output));
        catch ME
            clear server;
            rethrow(ME);
        end
        pause(0.1);
    end
    flush(server);
end
function naneyeTest()
    server = tcpserver("127.0.0.1",8888, "Timeout", 30);
    %flush(server);
    naneye = naneyeConstruct();
    disp("waiting for connection");
    while ~server.Connected
        pause(0.1);
    end
    disp("client connected");
    %{
    w = 250;
    h = 250;
    %}
    while true
        try
            output = outputdata(naneye);
            disp(output);
            write(server, output);
            %{
            % Write the data to the text file
            b = reshape(output(1:4:end), [w,h])';
            g = reshape(output(2:4:end), [w,h])';
            r = reshape(output(3:4:end), [w,h])';
            
            imgh = cat(3, r,g,b);
            writematrix(r, "out_matlab_r.txt", 'delimiter', '\t');
            writematrix(g, "out_matlab_g.txt", 'delimiter', '\t');
            writematrix(b, "out_matlab_b.txt", 'delimiter', '\t');
            %disp(size(output));
            %}
        catch ME
            clear server;
            rethrow(ME);
        end
        pause(0.1);
    end
    flush(server);
end
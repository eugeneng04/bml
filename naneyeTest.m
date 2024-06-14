function naneyeTest(first_pass)
    global imgh
    naneye = naneyeConstruct();
    
    %{
    w = 250;
    h = 250;
    %}
    naneye.StartCapture();
    %{
    global lh1
    global imgh
    %}
    lh1 = addlistener(naneye, 'ImageProcessed', @(o,e)ouputObj(e));
    if ~first_pass
        server = tcpserver("127.0.0.1",8888, "Timeout", 30);
        disp("waiting for connection");
        while ~server.Connected
            pause(0.1);
        end
        disp("client connected");
        while true
            output = imgh;
            %disp(output);
            if ~isempty(output)
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
            else
                disp("no video output");
            end
        end
    end
end

%{
function output = outputdata(naneye)
    %global lh1
    %lh1 = addlistener(naneye, 'ImageProcessed', @(o,e)ouputObj(e));
    output = imgh;
    return;
end
%}

function ouputObj(inbytes)
    global imgh
    imgh = uint8(inbytes.GetImageData.GetProcessedDataARGBByte);
end

%{
function output = getData()
   %global lh1
   global imgh
   output = imgh;
   %delete(lh1);
   return;
end
%}

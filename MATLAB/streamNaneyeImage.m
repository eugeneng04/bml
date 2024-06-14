function streamNaneyeImage(first_pass)
    global imgh
    naneye = naneyeConstruct();
   
    if ~first_pass
        naneye.StartCapture();
        lh1 = addlistener(naneye, 'ImageProcessed', @(o,e)ouputObj(e));
        server = tcpserver("127.0.0.1",8888, "Timeout", 30);
        disp("waiting for connection");
        while ~server.Connected
            pause(0.1);
        end
        disp("client connected");
        while true
            output = imgh;
            if ~isempty(output)
                try
                    write(server, output);
                catch ME
                    disp(ME);
                    break;
                end
            else
                server.delete();
                disp("Connection Error, Run Program again");
                break
            end
        end
    end
end

function ouputObj(inbytes)
    global imgh
    imgh = uint8(inbytes.GetImageData.GetProcessedDataARGBByte);
end
function output = outputdata(naneye)
    lh1 = addlistener(naneye, 'ImageProcessed', @(o,e)ouputObj(e));
    output = getData();
    disp("displaying output");
    disp(output);
    delete(lh1);
    return;
end

function ouputObj(inbytes)
    global hbytes
    hbytes = uint8(inbytes.GetImageData.GetProcessedDataARGBByte);
    disp(hbytes);
end

function output = getData()
   global hbytes
   output = hbytes;
   return;
end

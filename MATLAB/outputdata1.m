function output = outputdata1(naneye)
    naneye.StartCapture();
    %global lh1
    %lh1 = addlistener(naneye, 'ImageProcessed', @(o,e)ouputObj(e));
    output = getData();
    return;
end

function ouputObj(inbytes)
    global imgh
    imgh = uint8(inbytes.GetImageData.GetProcessedDataARGBByte);
    
end

function output = getData()
   %global lh1
   global imgh
   output = imgh;
   %delete(lh1);
   return;
end

function displayobj(inbytes,handles)
% Function that displays the sensor's image. First grabs the values from
% the sensor and reshapes them in a 3 dimensions vector. 
global fullimage lock w h
    
hbytes=uint8(inbytes.GetImageData.GetProcessedDataARGBByte);
b = reshape(hbytes(1:4:end), [w,h])';
g = reshape(hbytes(2:4:end), [w,h])';
r = reshape(hbytes(3:4:end), [w,h])';

imgh = cat(3, r,g,b);
pause(0.01); 
    
set(handles.image,'CData',imgh);
 
fullimage=imgh;

if lock == 3
    setgraph(handles,handles.axes2);
else
end
    
end
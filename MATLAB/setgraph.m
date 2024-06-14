function setgraph(handles,plotarea)
% This function sets the graph to be presented on axes2. case 1 corresponds
% to the normal histogram; case 2 to a 3D plot that has all the 250x250
% pixel values in red; case 3 is the same as case 2 but with the green
% values; and case 4 is also the same as the previous two plots, but for
% blue values.
% When the 'Color Reconstruction is deactivated, the 3D plot weights only
% the gray values.
%
global fullimage presenting_mode BW limitation

workingImage=fullimage;
popup_sel_index = get(handles.scriptlist, 'Value');

switch popup_sel_index
    case 1
        %histogram
        allvalues = reshape(workingImage,numel(workingImage),1);
        maxi=max(allvalues);
        mini=min(allvalues);
        edges = mini:1:maxi;
        counts=histc(allvalues,edges);

        if presenting_mode == 1
            histogr=counts./sum(counts);           
        else
            histogr=counts;
        end

        bar(plotarea,edges,histogr);
        grid(plotarea,'on');
        set(handles.axes2,'XLim',[0 260])

    case 2
        %red surf plot
        redvalues=workingImage(:,:,1);
        
        if BW == 0
            surf(plotarea,redvalues,'FaceColor',[1 0.38 0.38]);
            set(handles.axes2,'ZLim',[0 260])
            set(handles.axes2,'ZLimMode','manual')
        else
            surf(plotarea,redvalues);
            set(handles.axes2,'ZLim',[0 260])
            set(handles.axes2,'ZLimMode','manual')
        end
        
    case 3
        %green surf plot
        greenvalues=workingImage(:,:,2);
        surf(plotarea,greenvalues,'FaceColor',[0.32 1 0.41])
        set(handles.axes2,'ZLim',[0 260])
        set(handles.axes2,'ZLimMode','manual')
    case 4
        %blue surf plot
        bluevalues=workingImage(:,:,3);
        surf(plotarea,bluevalues,'FaceColor',[0.3 0.98 1])
        set(handles.axes2,'ZLim',[0 260])
        set(handles.axes2,'ZLimMode','manual')
end

% Defining the freezing of the axis to the maximum value.
if get(handles.axisauto,'Value') == 1
    set(handles.axes2,'YLim',limitation)
end

end
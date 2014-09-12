function showboxes(im, boxes, partcolor)

if nargin < 3,
  partcolor = {'g','g','y','m','m','m','m','y','y','y','r','r','r','r','y','c','c','c','c','y','y','y','b','b','b','b'};
end

imagesc(im); axis image; axis off;
if ~isempty(boxes)
  numparts = floor(size(boxes, 2)/4);
  for i = 1:numparts
    x1 = boxes(:,1+(i-1)*4);
    y1 = boxes(:,2+(i-1)*4);
    x2 = boxes(:,3+(i-1)*4);
    y2 = boxes(:,4+(i-1)*4);
    line([x1 x1 x2 x2 x1]',[y1 y2 y2 y1 y1]','color',partcolor{i},'linewidth',2);
  end
end
drawnow;
  
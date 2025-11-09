import torch
from torch.utils.data import Dataset

class SlicesDataset(Dataset):
    def __init__(self, data):
        self.data = data
        self.slices = []

        for i, d in enumerate(data):
            for j in range(d["image"].shape[0]):
                self.slices.append((i, j))

    def __getitem__(self, idx):

        slc = self.slices[idx]
        sample = dict()
        sample["id"] = idx

        image_idx, slice_idx = slc        
	
        slice_image  = self.data[image_idx]['image'][slice_idx] 
        slice_image = slice_image[None, :]                      

        slice_seg = self.data[image_idx]['seg'][slice_idx]        
        slice_seg = slice_seg[None, :]                          

        sample['image'] = torch.from_numpy(slice_image)         
        sample['seg'] = torch.from_numpy(slice_seg)             
        return sample

    def __len__(self):
        return len(self.slices)
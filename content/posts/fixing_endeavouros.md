---
title: "Fixing EndeavourOS boot failures"
author: "Edmund Goodman"
date: 2024-01-13T15:07:51Z
draft: false
---

This post enumerates a process which worked for me to repair an installation of EndeavourOS with full-disk encryption when it is unable to boot. It is also available [as a gist](https://gist.github.com/EdmundGoodman/c057ce0c826fd0edde7917d15b709f4f).

Specifically, this set of steps fixed the boot process on a HP-Envy laptop running EndeavourOS with an ext4 file system. The issue normally occurs after an interrupted update using `pacman -Syu`, which then causes the system to be unable to boot after the next restart (showing only "boot to firmware interface" in the boot menu).

## Steps to fix

### 1) Boot with an EndeavourOS live USB stick

You will need a live/bootable USB key with EndeavourOS installed on it. The [EndeavourOS website lists a number of ways to do this](https://discovery.endeavouros.com/installation/create-install-media-usb-key/2021/03/) {{< footnote "1" "<https://discovery.endeavouros.com/installation/create-install-media-usb-key/2021/03/)>" >}}.

Then, boot the computer from this live USB stick. This normally involves a process similar to:

1) Turning off the computer
2) Plugging in the USB stick
3) Turning on computer, then repeatedly pressing the ESC key, until a boot menu shows up
4) Navigate to select the boot device in the boot menu, then select the option to boot from the live USB

This should drop you into a working EndeavourOS operating system, from which you can run the steps to fix the broken one on the computer. All the next steps are commands to run in a terminal, which can be opened with `ctrl+alt+t`.

Additionally, you should connect to a WiFi network on the live boot, as this makes copy-pasting commands from the internet easier :sweat_smile:, and allows downloading/completing updates to the broken boot device.

### 2) Decrypt and mount the encrypted and boot disk partitions

First, identify your boot and encrypted partitions {{< footnote "2" "<https://linux.fernandocejas.com/docs/guides/mount-luks-partition-for-system-recovery#mount-luks-partitions-for-system-recovery>" >}}:

```bash
lsblk -f

```

This will list the available devices, from which you need to identify your boot and encrypted partitions. For my particular laptop:

- Encrypted partition = `nvme0n1p2`
- Boot partition = `nvme0n1p1`

Next, use `cryptsetup` to decrypt the LUKS encrypted drive {{< footnote "3" "<https://linux.fernandocejas.com/docs/guides/mount-luks-partition-for-system-recovery#1---open-the-encrypted-disk>" >}}:

```bash
sudo cryptsetup open /dev/mapper/nvme0n1p2 luks_root
```

Then, mount the newly decrypted partition and then the boot drive into the `/boot/` folder within it {{< footnote "4" "<https://linux.fernandocejas.com/docs/guides/mount-luks-partition-for-system-recovery#2---mount-all-the-partitions>" >}}:

```bash
sudo mount /dev/mapper/luks_root /mnt
sudo mount /dev/nvme0n1p1 /mnt/boot
```

### 3) Root into the broken system

**Before this step, it is helpful to have connected to the WiFi on the live boot, as you would on any Linux computer** {{< footnote "5" "It doesn't break anything if you don't connect to WiFi. However, if you later need WiFi access on the broken boot device you'll need to exit out, connect to WiFi, and `arch-chroot` back in if you haven't." >}}.

Next, use `arch-chroot` to root into the newly mounted broken system {{< footnote "6" "<https://linux.fernandocejas.com/docs/guides/mount-luks-partition-for-system-recovery#3---root-into-the-new-system>" >}}:

```bash
arch-chroot /mnt
```

### 4) Debugging WiFi inside `arch-chroot`

You can check whether WiFi is working inside `arch-chroot` using the `ping` command:

```bash
ping google.com
```

If the WiFi doesn't work inside `arch-chroot` on the broken device, first check if it is working on the live boot. If it isn't, fix it there, then exit and rerun `arch-chroot`.

If it still isn't working, the next most likely cause it DNS settings haven't been copied over. To fix this, exit the `arch-chroot` to unlock the `resolv.conf` file, add DNS settings, then rerun `arch-chroot` {{< footnote "7" "<https://unix.stackexchange.com/a/481862>" >}}:

```bash
exit
echo "nameserver 8.8.8.8" >> /mnt/etc/resolv.conf
arch-chroot /mnt
```

### 5) Try to repair the broken system

The common issues I have found across two failures are as follows:

- `pacman` was interrupted during running, so the lock file is still present {{< footnote "8" "<https://forum.endeavouros.com/t/update-problem-var-lib-pacman-db-lck/5239/2>" >}}
- `pacman` needs to finish the interrupted upgrade
- linux headers need to be re-installed
- `grub` needs to be re-built {{< footnote "9" "<https://wiki.archlinux.org/title/GRUB>" >}}

These can be resolved as follows (inside `arch-chroot` on the broken device):

```bash
sudo rm /var/lib/pacman/db.lck
sudo pacman -Syu
sudo pacman -Syu linux-lts linux-lts-headers
grub install --target=x86_54-efi --efi-directory=/boot/efi --bootloader-id=GRUB
grub-mkconfig -o /boot/grub/grub.cfg
```

It is possible something else is wrong, but this time is when you should largely be running commands to fix it!

Then, disconnect from the `arch-chroot` as follows:

```bash
exit
```

### 6) Clean up and try to boot

Before restarting, it is good practice to unmount both the boot and decrypted partitions, then close the decrypted partition {{< footnote "10" "<https://linux.fernandocejas.com/docs/guides/mount-luks-partition-for-system-recovery#4---unmount-and-exit>" >}}.

```bash
sudo umount /mnt/boot/
sudo umount /mnt
sudo cryptsetup close luks_root
```

Finally, restart the computer, and hope that it boots correctly!

```bash
reboot
```

## References

{{< footnote_list >}}

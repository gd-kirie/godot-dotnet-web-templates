#nullable enable
using System;
using System.Diagnostics;
using System.Threading;
using System.Threading.Tasks;
using Godot;
using Environment = System.Environment;

namespace Step1CSharpWeb;

public partial class Main : Control
{
    // Only the main thread touches Godot objects. Workers publish plain data.
    private sealed class Work
    {
        public int Id, Progress, Batches, Stop, State;
        public long Checksum;
        public string? Error;
        public readonly int DurationMs;
        public Work(int durationMs) => DurationMs = durationMs;
        public void Run()
        {
            try
            {
                Volatile.Write(ref Id, Environment.CurrentManagedThreadId);
                var clock = Stopwatch.StartNew();
                uint hash = 2463534242;
                while (clock.ElapsedMilliseconds < DurationMs && Volatile.Read(ref Stop) == 0)
                {
                    for (int i = 0; i < 32768; i++)
                    {
                        hash ^= hash << 13;
                        hash ^= hash >> 17;
                        hash ^= hash << 5;
                    }
                    Interlocked.Exchange(ref Checksum, hash);
                    Interlocked.Increment(ref Batches);
                    Volatile.Write(ref Progress, (int)Math.Min(99, clock.ElapsedMilliseconds * 100 / DurationMs));
                }
                bool cancelled = Volatile.Read(ref Stop) != 0;
                if (!cancelled) Volatile.Write(ref Progress, 100);
                Volatile.Write(ref State, cancelled ? 3 : 2);
            }
            catch (Exception ex)
            {
                Error = ex.Message;
                Volatile.Write(ref State, 4);
            }
        }
    }

    private readonly Label[] _names = new Label[2];
    private readonly Label[] _details = new Label[2];
    private readonly ProgressBar[] _bars = new ProgressBar[2];
    private Work[] _work = { new(4000), new(6000) };
    private Label _heartbeat = null!, _status = null!;
    private ProgressBar _pulse = null!;
    private Button _start = null!, _cancel = null!, _click = null!;
    private int _frames, _clicks, _mainId;
    private double _elapsed, _logTime;
    private bool _running;

    private T Place<T>(T control, float x, float y, float width, float height) where T : Control
    {
        control.Position = new Vector2(x, y);
        control.Size = new Vector2(width, height);
        AddChild(control);
        return control;
    }
    private Label TextAt(string text, float y, int size = 18, string color = "dce6f4")
    {
        var label = Place(new Label { Text = text }, 48, y, 864, 28);
        label.AddThemeFontSizeOverride("font_size", size);
        label.AddThemeColorOverride("font_color", new Color(color));
        return label;
    }

    public override void _Ready()
    {
        AddChild(new ThreadProbe());
        _mainId = Environment.CurrentManagedThreadId;
        Place(new ColorRect { Color = new Color("101827"), MouseFilter = MouseFilterEnum.Ignore }, 0, 0, 960, 540);
        TextAt("Two C# workers. One responsive UI.", 24, 32);
        TextAt("Real CPU work: xorshift calculations for 4 s / 6 s. Progress = elapsed budget.", 68, 17, "9aa8bc");
        _heartbeat = TextAt("", 103, 18, "8bd5ff");
        _pulse = Place(new ProgressBar { ShowPercentage = false }, 48, 137, 864, 8);
        for (int i = 0; i < 2; i++)
        {
            float y = 165 + i * 108;
            _names[i] = TextAt(i == 0 ? "A / new Thread — ready" : "B / Task.Run — ready", y, 22);
            _bars[i] = Place(new ProgressBar(), 48, y + 34, 864, 22);
            _details[i] = TextAt("Waiting for Start", y + 62, 16, "9aa8bc");
        }
        _start = Place(new Button { Text = "Start both workers" }, 48, 385, 260, 52);
        _cancel = Place(new Button { Text = "Cancel", Disabled = true }, 324, 385, 180, 52);
        _click = Place(new Button { Text = "UI clicks: 0 — try me while running" }, 520, 385, 392, 52);
        _start.Pressed += StartWork;
        _cancel.Pressed += () =>
        {
            foreach (var work in _work) Volatile.Write(ref work.Stop, 1);
            _cancel.Disabled = true;
        };
        _click.Pressed += () =>
        {
            _click.Text = $"UI clicks: {++_clicks} — try me while running";
            GD.Print($"DEMO_CLICK count={_clicks} running={_running}");
        };
        _status = TextAt("Start the workers, then keep clicking. Watch the main-thread heartbeat above.", 451, 17);
        TextAt("Godot 4.7.2 / .NET 10.0.12 / Wasm threads  ·  Thread IDs are managed IDs.", 487, 16, "9aa8bc");
        GD.Print($"DEMO_READY main={_mainId}");
    }

    private void StartWork()
    {
        if (_running) return;
        _work = new[] { new Work(4000), new Work(6000) };
        _running = true;
        _start.Disabled = true;
        _cancel.Disabled = false;
        _status.Text = "Both workers are computing. The UI keeps processing frames and clicks.";
        try
        {
            Volatile.Write(ref _work[0].State, 1);
            new System.Threading.Thread(_work[0].Run) { IsBackground = true }.Start();
        }
        catch (Exception ex)
        {
            _work[0].Error = ex.Message;
            Volatile.Write(ref _work[0].State, 4);
            GD.Print("DEMO_FAIL " + ex);
        }
        try
        {
            Volatile.Write(ref _work[1].State, 1);
            _ = Task.Run(_work[1].Run);
        }
        catch (Exception ex)
        {
            _work[1].Error = ex.Message;
            Volatile.Write(ref _work[1].State, 4);
            GD.Print("DEMO_FAIL " + ex);
        }
        GD.Print("DEMO_STARTED");
    }

    public override void _Process(double delta)
    {
        _elapsed += delta;
        _logTime += delta;
        _heartbeat.Text = $"MAIN THREAD #{_mainId}    frame {++_frames:N0}    alive {_elapsed:0.0} s";
        _pulse.Value = (_elapsed % 2) * 50;
        for (int i = 0; i < 2; i++)
        {
            var work = _work[i];
            int state = Volatile.Read(ref work.State);
            string status = state switch { 1 => "computing", 2 => "complete", 3 => "cancelled", 4 => "failed", _ => "ready" };
            _names[i].Text = $"{(i == 0 ? "A / new Thread" : "B / Task.Run")}    #{Volatile.Read(ref work.Id)}    {status}";
            _bars[i].Value = Volatile.Read(ref work.Progress);
            _details[i].Text = state == 4 ? work.Error : $"{Volatile.Read(ref work.Batches) * 32768L:N0} calculations    checksum {Interlocked.Read(ref work.Checksum):X8}";
        }
        if (_running && _logTime >= 0.5)
        {
            _logTime = 0;
            GD.Print($"DEMO_STATE frames={_frames} a={_bars[0].Value} b={_bars[1].Value} aid={Volatile.Read(ref _work[0].Id)} bid={Volatile.Read(ref _work[1].Id)} acount={Volatile.Read(ref _work[0].Batches)} bcount={Volatile.Read(ref _work[1].Batches)}");
        }
        if (_running && Volatile.Read(ref _work[0].State) >= 2 && Volatile.Read(ref _work[1].State) >= 2)
        {
            _running = false;
            _start.Disabled = false;
            _cancel.Disabled = true;
            bool completed = _work[0].State == 2 && _work[1].State == 2;
            _status.Text = completed ? "Both workers finished. Click Start to run again." : "Workers stopped. Click Start to run again.";
            GD.Print(completed ? "DEMO_COMPLETE" : "DEMO_STOPPED");
        }
    }
    public override void _ExitTree()
    {
        foreach (var work in _work) Volatile.Write(ref work.Stop, 1);
    }
}
